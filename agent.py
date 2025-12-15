import json
import datetime
import re
from llm_core import OpenAIProvider
from tools import registry
from memory import MemoryManager

class Agent:
    def __init__(self, llm: OpenAIProvider, user_id: str):
        self.llm = llm
        self.memory = MemoryManager(user_id)
        
    def _construct_system_prompt(self):
        current_time = datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        profile_str, _ = self.memory.get_context()
        
        return f"""你是一个智能助手。当前时间：{current_time}。

【长期记忆】：
{profile_str}

【你的能力】：
1. **搜索能力**：遇到不知道的事实（天气、新闻、定义），请调用 `search_knowledge`。
2. **记忆能力**：如果用户提到他的个人信息（名字、爱好、居住地），请务必调用 `save_user_info` 工具保存。

请根据用户的偏好进行个性化回复。
"""

    def _try_parse_deepseek_xml(self, content):
        # ... (保留之前的 DeepSeek 补丁代码，不用变) ...
        # 为了节省篇幅，这里省略，请保留你之前文件里的这个函数
        if not content or "<｜DSML｜invoke" not in content: return None
        try:
            func_match = re.search(r'name="([^"]+)"', content)
            if not func_match: return None
            func_name = func_match.group(1)
            
            # 增强解析：同时支持 query (搜索) 和 key/value (记忆)
            args = {}
            if "parameter name=\"query\"" in content:
                q = re.search(r'parameter name="query".*?>([^<]+)<', content)
                if q: args["query"] = q.group(1)
            
            if "parameter name=\"key\"" in content:
                k = re.search(r'parameter name="key".*?>([^<]+)<', content)
                v = re.search(r'parameter name="value".*?>([^<]+)<', content)
                if k and v: 
                    args["key"] = k.group(1)
                    args["value"] = v.group(1)

            return [{"id": "patch", "function": {"name": func_name, "arguments": json.dumps(args)}}]
        except: return None

    def run(self, user_input: str):
        self.memory.add_message("user", user_input)
        
        # --- 移除旧的 if "我喜欢" 代码，完全交给 LLM ---

        messages = [{"role": "system", "content": self._construct_system_prompt()}] + self.memory.get_context()[1]

        response = self.llm.chat_completion(messages, tools=registry.tool_definitions)
        response_msg = response.choices[0].message
        
        tool_calls = response_msg.tool_calls
        content = response_msg.content

        # DeepSeek 补丁逻辑
        if not tool_calls and content:
            tool_calls = self._try_parse_deepseek_xml(content)

        if tool_calls:
            # 将思考过程加入历史
            messages.append(response_msg)
            
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                    
                    # === 关键修改：拦截记忆工具 ===
                    if func_name == "save_user_info":
                        # 直接调用 memory 模块的方法
                        self.memory.update_preference(args["key"], args["value"])
                        tool_result = f"系统提示：已成功保存用户记忆 [{args['key']} = {args['value']}]"
                    else:
                        # 其他工具（如搜索）走通用流程
                        tool_result = registry.execute(func_name, **args)
                        
                except Exception as e:
                    tool_result = f"Tool Error: {e}"
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id if hasattr(tool_call, 'id') else "patch_id",
                    "content": str(tool_result)
                })
            
            # 工具执行后，让 LLM 生成最终回复
            final_resp = self.llm.chat_completion(messages)
            final_content = final_resp.choices[0].message.content
        else:
            final_content = content

        self.memory.add_message("assistant", final_content)
        return final_content
import json
import datetime
import re # 新增：用于正则解析 DeepSeek 的原始标签
from llm_core import OpenAIProvider
from tools import registry
from memory import MemoryManager

class Agent:
    def __init__(self, llm: OpenAIProvider, user_id: str):
        self.llm = llm
        self.memory = MemoryManager(user_id)
        
    def _construct_system_prompt(self):
        # 1. 获取当前精确时间
        current_time = datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        
        profile_str, _ = self.memory.get_context()
        base_prompt = f"""你是一个智能助手。
当前系统时间是：{current_time}
（如果用户询问时间，请以该系统时间为准）

1. 请根据用户的历史偏好（User Profile）进行个性化回答。
2. 你拥有搜索工具，当问题涉及事实性知识（如天气、股票、定义、实时信息）时，请务必调用搜索工具。
3. 遇到不知道的问题，不要瞎编，请尝试搜索。
"""
        return f"{base_prompt}\n{profile_str}"

    # 新增：DeepSeek 原始标签解析补丁
    def _try_parse_deepseek_xml(self, content):
        """
        当 DeepSeek 未正确触发 tool_calls 字段，而是直接在 content 输出 XML 时，
        尝试手动解析。
        格式示例: <｜DSML｜invoke name="search_knowledge"><｜DSML｜parameter name="query"...>
        """
        if not content or "<｜DSML｜invoke" not in content:
            return None
            
        try:
            # 简单正则匹配 invoke name
            func_match = re.search(r'name="([^"]+)"', content)
            if not func_match: return None
            func_name = func_match.group(1)
            
            # 简单正则匹配 parameter query (针对 search_knowledge 工具的简化解析)
            # 注意：这只是一个简易补丁，复杂的参数建议使用更严谨的 XML 解析
            param_match = re.search(r'parameter name="query".*?>([^<]+)<', content)
            if not param_match: return None
            query_val = param_match.group(1)
            
            # 构造模拟的 tool_call 对象
            return [{
                "id": "call_patch_" + datetime.datetime.now().strftime("%f"),
                "function": {
                    "name": func_name,
                    "arguments": json.dumps({"query": query_val})
                }
            }]
        except Exception as e:
            print(f"[Patch Error] 解析 DeepSeek XML 失败: {e}")
            return None

    def run(self, user_input: str):
        self.memory.add_message("user", user_input)
        
        # 简单的记忆触发逻辑修正 (防止 "你还记得我喜欢什么吗" 误触发)
        if "我喜欢" in user_input and "你还记得" not in user_input:
             # 简单提取逻辑
             pass

        system_msg = {"role": "system", "content": self._construct_system_prompt()}
        _, history = self.memory.get_context()
        messages = [system_msg] + history

        # 调用 LLM
        response = self.llm.chat_completion(messages, tools=registry.tool_definitions)
        response_msg = response.choices[0].message
        
        tool_calls = response_msg.tool_calls
        content = response_msg.content

        # 【关键修复】如果 tool_calls 为空，但 content 里有 DeepSeek 的 XML 标签，手动解析
        if not tool_calls and content:
            tool_calls_patch = self._try_parse_deepseek_xml(content)
            if tool_calls_patch:
                print(f"[System] 检测到 DeepSeek 原始 XML，已启动兼容模式。")
                tool_calls = [] # 构造伪造的对象结构
                # 这里需要把 patch 转换成类似 OpenAI 对象，或者调整下面的逻辑
                # 为了保持代码简洁，我们在下面直接用 dict 处理
                for patch in tool_calls_patch:
                    # 构造一个兼容对象
                    class MockToolCall:
                        def __init__(self, d):
                            self.id = d['id']
                            self.function = type('obj', (object,), {
                                'name': d['function']['name'],
                                'arguments': d['function']['arguments']
                            })
                    tool_calls.append(MockToolCall(patch))

        # 处理工具调用
        if tool_calls:
            messages.append(response_msg) 
            
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                    tool_result = registry.execute(func_name, **args)
                except Exception as e:
                    tool_result = f"Error executing tool: {e}"
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result)
                })
            
            # 再次调用 LLM
            final_response = self.llm.chat_completion(messages)
            final_content = final_response.choices[0].message.content
        else:
            final_content = content

        # 简单的偏好提取演示
        if "我喜欢" in user_input and "你还记得" not in user_input:
             topic = user_input.split("我喜欢")[-1].strip("。")
             self.memory.update_preference("hobby", topic)

        self.memory.add_message("assistant", final_content)
        return final_content
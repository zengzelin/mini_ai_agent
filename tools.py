import json
import datetime

from duckduckgo_search import DDGS


# 模拟的本地文档数据库
MOCK_KNOWLEDGE_BASE = {
    "天气": "查询天气请提供具体城市。目前库中仅包含：北京、上海、西安。",
    "西安": "西安今日天气：晴转多云，气温 18-26 度，微风，空气质量优。",
    "股票": "科技股今日大涨，纳斯达克指数上涨 2%。",
    "DeepSeek": "DeepSeek 是一家专注于AGI研究的中国人工智能公司，其模型在推理和代码方面表现出色。",
    "日期": f"本地数据库暂存日期为 {datetime.datetime.now().strftime('%Y-%m-%d')} (模拟数据)",
    "Agent": "Agent 是一种能够感知环境、进行推理并采取行动的智能体。"
}

class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.tool_definitions = []

    def register(self, func, name, description, parameters):
        self.tools[name] = func
        self.tool_definitions.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        })
    
    def execute(self, name, **kwargs):
        if name in self.tools:
            return self.tools[name](**kwargs)
        return f"Error: Tool {name} not found."

def internet_search_func(query: str):
    print(f"\n[System] 正在联网搜索: {query} ...")
    results = []
    
    try:
        # 【修改点】最新版写法：直接实例化 DDGS，不使用 with 语句
        ddgs = DDGS()
        
        # text() 方法返回的是一个生成器或列表
        ddg_results = ddgs.text(query, max_results=3)
            
        if not ddg_results:
            return "未找到相关网络搜索结果。"

        # 遍历结果
        for idx, res in enumerate(ddg_results):
            title = res.get('title', 'No Title')
            body = res.get('body', 'No Content')
            href = res.get('href', '')
            results.append(f"结果 {idx+1}:\n标题: {title}\n内容: {body}\n链接: {href}\n")
            
        return "\n".join(results)

    except Exception as e:
        print(f"[Search Error] {e}") # 打印错误方便调试
        return f"搜索出错: {str(e)}"

# --- 注册 ---
registry = ToolRegistry()
registry.register(
    func=internet_search_func, # 替换为新的联网函数
    name="search_knowledge",   # 名字保持不变，这样 agent.py 不用改
    description="这是一个联网搜索引擎。当用户询问实时新闻、天气、百科知识或任何你不知道的事实时，请使用此工具。",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "用于搜索引擎的关键词，尽量精准"}
        },
        "required": ["query"]
    }
)
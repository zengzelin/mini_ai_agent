# Mini AI Agent Framework

这是一个基于 Python 实现的轻量级通用 AI Agent 框架。它具备多轮对话能力、联网搜索能力以及基于用户偏好的长期记忆功能。

该项目旨在展示如何不依赖庞大的框架（如 LangChain），仅使用原生 Python 和 OpenAI SDK 构建一个具备 **Function Calling (工具调用)**、**Memory (记忆)** 和 **LLM Management (模型管理)** 的智能体。

## ✨ 核心特性

- **🧠 智能对话与上下文**: 自动维护短期对话历史，支持连贯的多轮交互。
- **🌐 联网搜索能力**: 
  - 集成 `duckduckgo-search`，Agent 可自主判断何时搜索实时信息（如天气、股票、新闻）。
  - 支持 DeepSeek 等模型的 Function Calling 原始 XML 格式解析补丁。
- **💾 长期记忆系统 (Memory)**: 
  - 自动识别用户偏好（如“我喜欢...”），并持久化存储到 JSON 文件。
  - 在后续对话中自动加载用户画像，实现个性化回复。
- **🔌 模型无关设计**: 
  - 抽象 `LLMProvider` 层，可轻松切换 OpenAI、DeepSeek、Moonshot 等兼容 OpenAI 格式的 API。

## 🛠️ 文件结构

```text
.
├── main.py           # 程序入口，处理用户输入循环
├── agent.py          # Agent 核心类，串联 LLM、Memory 和 Tools
├── llm_core.py       # LLM 接口抽象与实现 (LLM Management)
├── memory.py         # 记忆管理 (Session Context & User Profile)
├── tools.py          # 工具注册表与联网搜索实现
├── requirements.txt  # 项目依赖
└── README.md         # 项目文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

在 [main.py](main.py) 中设置你的 API Key 和 Base URL：

```python
# 使用 DeepSeek API
API_KEY = "your-deepseek-api-key"
BASE_URL = "https://api.deepseek.com"

# 或使用 OpenAI API
# API_KEY = "your-openai-api-key"
# BASE_URL = None  # 使用默认 OpenAI 端点
```

也可以通过环境变量设置：

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.deepseek.com"
```

### 3. 运行程序

```bash
python main.py
```

## 💡 使用示例

### 基础对话
```
User: 你好！
Agent: 你好！有什么我可以帮助你的吗？
```

### 搜索功能
```
User: 今天北京的天气怎么样？
Agent: [自动调用联网搜索工具]
      北京今日天气：晴，气温15-25度...
```

### 记忆功能
```
User: 我喜欢吃火锅
Agent: 好的，我已经记住你喜欢吃火锅了！

User: 我的兴趣爱好有哪些？
Agent: 根据我的记忆，你喜欢吃火锅。
```

记忆会自动保存到 `user_profile.json` 文件中：

```json
{
  "user_001": {
    "hobby": "吃火锅",
    "name": "张三",
    "location": "北京"
  }
}
```

## 🏗️ 架构设计

### 核心模块

1. **LLM Management (`llm_core.py`)**
   - 抽象 LLM 接口，支持多种模型提供商
   - 统一的 `chat_completion` 调用方式

2. **Agent Core (`agent.py`)**
   - 对话流程控制
   - 工具调用判断与执行
   - DeepSeek XML 格式兼容补丁

3. **Memory System (`memory.py`)**
   - 短期记忆：维护对话历史上下文
   - 长期记忆：持久化用户偏好到 JSON

4. **Tools Registry (`tools.py`)**
   - 工具注册与执行
   - 联网搜索实现（基于 DuckDuckGo）

## 🔧 工具系统

### 已实现的工具

1. **search_knowledge** - 联网搜索
   - 自动检测需要搜索的场景
   - 返回前3条相关结果

2. **save_user_info** - 保存用户信息
   - 自动提取用户偏好
   - 持久化到 JSON 文件

### 添加自定义工具

在 `tools.py` 中注册新工具：

```python
def my_custom_tool(param1: str):
    # 你的工具逻辑
    return f"处理结果: {param1}"

registry.register(
    func=my_custom_tool,
    name="my_tool",
    description="工具描述",
    parameters={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "参数说明"}
        },
        "required": ["param1"]
    }
)
```

## 📝 技术要点

### Function Calling 实现

项目使用 OpenAI 的 Function Calling 机制，但也兼容 DeepSeek 的 XML 格式：

```python
# DeepSeek 可能返回这样的格式：
<｜DSML｜invoke name="search_knowledge">
<parameter name="query">北京天气</parameter>
</｜DSML｜>

# 项目会自动转换为标准的 tool_calls 格式
```

### 记忆系统设计

- **短期记忆**：保留最近 10 条消息（5 轮对话）
- **长期记忆**：基于 JSON 文件的简单 KV 存储
- 支持多用户隔离（通过 `user_id`）

## 🎯 待扩展功能

- [ ] 向量数据库集成（用于语义搜索）
- [ ] 更多工具：天气查询、日历管理等
- [ ] 流式输出支持
- [ ] Web UI 界面
- [ ] 对话历史导出

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
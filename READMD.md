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
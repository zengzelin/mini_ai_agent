import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any

# 抽象基类
class LLMProvider(ABC):
    @abstractmethod
    def chat_completion(self, messages: List[Dict[str, str]], tools: List[Dict] = None) -> Any:
        pass

# OpenAI 实现 (也可以轻易扩展为 Claude, DeepSeek 等)
class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def chat_completion(self, messages: List[Dict[str, str]], tools: List[Dict] = None) -> Any:
        # 处理参数，如果tools为空则不传，避免API报错
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7
        }
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
            
        return self.client.chat.completions.create(**params)
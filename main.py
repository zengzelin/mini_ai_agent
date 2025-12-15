import os
from llm_core import OpenAIProvider
from agent import Agent

# 请替换为你的 API Key
# 也可以使用兼容 OpenAI 格式的其他服务商，如 DeepSeek, Moonshot 等
API_KEY = os.getenv("OPENAI_API_KEY", "sk-c213c77b6840422196582131240a4232") 
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")

def main():
    print("=== 通用对话 Agent (具备搜索与记忆能力) ===")
    print("输入 'exit' 退出\n")

    # 初始化 LLM Provider (LLM Management)
    llm = OpenAIProvider(api_key=API_KEY, base_url=BASE_URL, model="deepseek-chat")
    
    # 初始化 Agent，假设用户ID为 user_001
    agent = Agent(llm, user_id="user_001")

    while True:
        try:
            q = input("User: ")
            if q.lower() in ["exit", "quit"]:
                break
            
            if not q.strip():
                continue

            response = agent.run(q)
            print(f"Agent: {response}\n")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
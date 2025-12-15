import json
import os

class MemoryManager:
    def __init__(self, user_id: str, profile_path="user_profile.json"):
        self.user_id = user_id
        self.profile_path = profile_path
        self.short_term_history = [] # 必做项 1: 上下文保持
        self.user_profile = self._load_profile() # 加分项 1.1: 长期记忆

    def _load_profile(self):
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get(self.user_id, {})
            except:
                return {}
        return {}

    def save_profile(self):
        # 简单实现：读取全部，更新当前用户，写回
        all_data = {}
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, 'r', encoding='utf-8') as f:
                    all_data = json.load(f)
            except:
                pass
        all_data[self.user_id] = self.user_profile
        with open(self.profile_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

    def add_message(self, role, content):
        self.short_term_history.append({"role": role, "content": content})
        # 限制历史长度，保持最近 N 轮 (这里取最近10条消息，即5轮)
        if len(self.short_term_history) > 10:
            self.short_term_history = self.short_term_history[-10:]

    def get_context(self):
        # 将长期记忆注入到 System Prompt 或作为上下文的一部分
        profile_str = f"User Profile: {json.dumps(self.user_profile, ensure_ascii=False)}" if self.user_profile else ""
        return profile_str, self.short_term_history

    def update_preference(self, key, value):
        print(f"[Memory] 更新用户画像: {key} -> {value}")
        self.user_profile[key] = value
        self.save_profile()
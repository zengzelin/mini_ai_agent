"""
测试 Memory 模块的功能
验证 JSON 文件是否能正常生成和读取
"""
from memory import MemoryManager
import os

def test_memory():
    print("=== 测试 Memory 模块 ===\n")
    
    # 1. 创建 Memory Manager
    print("1. 创建 MemoryManager (user_id=test_user)")
    mem = MemoryManager("test_user", profile_path="test_profile.json")
    
    # 2. 添加用户信息
    print("\n2. 添加用户信息...")
    mem.update_preference("name", "测试用户")
    mem.update_preference("hobby", "编程")
    mem.update_preference("location", "北京")
    
    # 3. 检查文件是否生成
    print("\n3. 检查 JSON 文件...")
    if os.path.exists("test_profile.json"):
        print("✅ test_profile.json 文件已生成！")
        with open("test_profile.json", 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"文件内容：\n{content}")
    else:
        print("❌ 文件未生成！")
    
    # 4. 测试记忆读取
    print("\n4. 测试记忆读取...")
    profile_str, history = mem.get_context()
    print(f"用户画像：{profile_str}")
    
    # 5. 创建新的 Manager 实例测试持久化
    print("\n5. 重新加载测试...")
    mem2 = MemoryManager("test_user", profile_path="test_profile.json")
    print(f"重新加载的用户信息: {mem2.user_profile}")
    
    # 清理测试文件
    print("\n6. 清理测试文件...")
    if os.path.exists("test_profile.json"):
        os.remove("test_profile.json")
        print("✅ 测试完成，已清理测试文件")

if __name__ == "__main__":
    test_memory()

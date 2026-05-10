"""
测试LLM配置管理器

**用途**：
- 验证配置文件加载
- 测试模型切换
- 查看使用量统计
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.llm_config_manager import llm_config_manager


def test_config_loading():
    """测试配置加载"""
    print("\n" + "=" * 80)
    print("测试1: 配置加载")
    print("=" * 80)
    
    multi_config = llm_config_manager.multi_provider_config
    if multi_config:
        print(f"✅ 配置加载成功")
        print(f"   提供商数量: {len(multi_config.providers)}")
        
        for i, provider in enumerate(multi_config.providers, 1):
            print(f"\n   提供商 {i}: {provider.name}")
            print(f"     Base URL: {provider.baseUrl}")
            print(f"     API协议: {provider.api}")
            print(f"     优先级: {provider.priority}")
            print(f"     模型数量: {len(provider.models)}")
            
            for j, model in enumerate(provider.models, 1):
                print(f"\n       模型 {j}:")
                print(f"         ID: {model.id}")
                print(f"         名称: {model.name}")
                print(f"         启用: {'是' if model.enabled else '否'}")
                print(f"         每日限制: {model.dailyTokenLimit:,} tokens")
                print(f"         可用: {'是' if model.can_use() else '否'}")
    else:
        print("❌ 配置加载失败")


def test_current_model():
    """测试当前模型选择"""
    print("\n" + "=" * 80)
    print("测试2: 当前模型")
    print("=" * 80)
    
    current = llm_config_manager.get_current_model()
    if current:
        print(f"✅ 当前模型: {current.name}")
        print(f"   ID: {current.id}")
        print(f"   上下文窗口: {current.contextWindow:,}")
        print(f"   最大输出: {current.maxTokens:,}")
    else:
        print("❌ 没有可用的模型")


def test_model_switching():
    """测试模型切换"""
    print("\n" + "=" * 80)
    print("测试3: 模型切换")
    print("=" * 80)
    
    current_before = llm_config_manager.get_current_model()
    if not current_before:
        print("⚠️  没有当前模型，跳过测试")
        return
    
    print(f"切换前: {current_before.name}")
    
    success = llm_config_manager.switch_to_next_model()
    if success:
        current_after = llm_config_manager.get_current_model()
        print(f"✅ 切换成功: {current_after.name}")
        
        # 切换回来
        llm_config_manager.switch_to_next_model()
        print(f"   已切换回原模型")
    else:
        print("❌ 切换失败（可能只有一个模型）")


def test_usage_tracking():
    """测试使用量跟踪"""
    print("\n" + "=" * 80)
    print("测试4: 使用量跟踪")
    print("=" * 80)
    
    current = llm_config_manager.get_current_model()
    if not current:
        print("⚠️  没有当前模型，跳过测试")
        return
    
    print(f"模型: {current.name}")
    print(f"当前使用量: {current.used_tokens_today:,} tokens")
    print(f"每日限制: {current.dailyTokenLimit:,} tokens")
    print(f"剩余可用: {current.dailyTokenLimit - current.used_tokens_today:,} tokens")
    
    # 模拟记录使用
    test_tokens = 1000
    print(f"\n模拟记录 {test_tokens:,} tokens...")
    llm_config_manager.record_token_usage(test_tokens)
    
    current = llm_config_manager.get_current_model()
    print(f"更新后使用量: {current.used_tokens_today:,} tokens")
    print(f"✅ 使用量跟踪正常")


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("LLM配置管理器测试")
    print("=" * 80)
    
    try:
        test_config_loading()
        test_current_model()
        test_model_switching()
        test_usage_tracking()
        
        print("\n" + "=" * 80)
        print("✅ 所有测试完成！")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

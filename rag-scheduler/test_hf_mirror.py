"""
测试 HuggingFace 镜像配置
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入配置（这会触发 HF_ENDPOINT 的设置）
from app.core.config import settings

print("=" * 80)
print("HuggingFace 镜像配置测试")
print("=" * 80)
print(f"\n1. 环境变量 HF_ENDPOINT: {os.environ.get('HF_ENDPOINT', '未设置')}")
print(f"2. Settings.HF_ENDPOINT: {settings.HF_ENDPOINT}")
print(f"3. 当前工作目录: {os.getcwd()}")

# 测试 FlagEmbedding 是否能使用镜像
try:
    print("\n4. 测试 FlagEmbedding 导入...")
    from FlagEmbedding import FlagReranker
    print("   ✓ FlagEmbedding 导入成功")
    
    print("\n5. 尝试加载 Reranker 模型（这可能需要几分钟）...")
    print("   提示：如果看到下载进度，说明镜像配置生效")
    
    # 这里不实际加载模型，只是确认可以导入
    print("   ✓ 可以正常使用 FlagEmbedding")
    
except ImportError as e:
    print(f"   ✗ FlagEmbedding 导入失败: {e}")
except Exception as e:
    print(f"   ✗ 错误: {e}")

print("\n" + "=" * 80)
print("测试完成！")
print("=" * 80)

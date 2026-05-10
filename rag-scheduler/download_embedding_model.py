"""
预下载 Embedding 模型到本地 models 目录

使用说明：
1. 首次运行前确保已配置 HuggingFace 镜像（.env 中的 HF_ENDPOINT）
2. 运行此脚本会自动下载模型到 ./models/all-MiniLM-L6-v2
3. 下载完成后，服务启动时将直接使用本地模型，无需联网

使用方法：
    python download_embedding_model.py
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量（必须在导入其他模块之前）
from dotenv import load_dotenv
load_dotenv()

# 设置 HuggingFace 镜像
os.environ["HF_ENDPOINT"] = os.getenv("HF_ENDPOINT", "https://hf-mirror.com")
print(f"使用 HuggingFace 镜像: {os.environ['HF_ENDPOINT']}")


def download_model():
    """下载 Embedding 模型到本地目录"""
    from sentence_transformers import SentenceTransformer
    
    # 模型名称和路径
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    local_path = project_root / "models" / "all-MiniLM-L6-v2"
    
    print("=" * 80)
    print("KRET-RAG Embedding 模型下载工具")
    print("=" * 80)
    print()
    print(f"模型名称: {model_name}")
    print(f"本地路径: {local_path}")
    print()
    
    # 检查模型是否已存在
    if local_path.exists():
        print(f"✅ 模型已存在于本地: {local_path}")
        print()
        
        # 询问是否重新下载
        response = input("是否重新下载？(y/n): ").strip().lower()
        if response != 'y':
            print("取消下载")
            return
        
        print("开始重新下载...")
        print()
    
    try:
        print("正在下载模型（约100MB），请耐心等待...")
        print("提示：首次下载可能需要几分钟时间")
        print()
        
        # 下载模型
        model = SentenceTransformer(model_name)
        
        # 保存到本地路径
        print(f"正在保存模型到: {local_path}")
        model.save(str(local_path))
        
        print()
        print("=" * 80)
        print("✅ 模型下载成功！")
        print("=" * 80)
        print()
        print(f"模型路径: {local_path}")
        print()
        print("下一步操作：")
        print("1. 确认 .env 文件中 EMBEDDING_MODEL=./models/all-MiniLM-L6-v2")
        print("2. 启动服务: .\\start-scheduler.bat")
        print("3. 服务将直接使用本地模型，无需联网下载")
        print()
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ 模型下载失败")
        print("=" * 80)
        print()
        print(f"错误信息: {str(e)}")
        print()
        print("可能的原因：")
        print("1. 网络连接问题 - 请检查网络或配置镜像")
        print("2. 磁盘空间不足 - 需要至少 500MB 空间")
        print("3. 权限问题 - 请确保有写入权限")
        print()
        print("建议解决方案：")
        print("1. 检查 .env 文件中的 HF_ENDPOINT 配置")
        print("2. 尝试使用其他镜像地址")
        print("3. 手动下载模型并放置到 models 目录")
        print()
        raise


if __name__ == "__main__":
    try:
        download_model()
    except KeyboardInterrupt:
        print("\n\n用户取消下载")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序异常: {str(e)}")
        sys.exit(1)

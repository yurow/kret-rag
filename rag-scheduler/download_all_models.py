"""
下载所有 RAG 所需的模型到本地

功能：
- 下载 Embedding 模型（all-MiniLM-L6-v2）
- 下载 Reranker 模型（BAAI/bge-reranker-base）
- 验证模型完整性
- 配置使用本地路径

使用方法：
    python download_all_models.py
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))


def download_embedding_model():
    """下载 Embedding 模型"""
    print("\n" + "=" * 80)
    print("1. 下载 Embedding 模型")
    print("=" * 80)
    
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    local_path = "./models/all-MiniLM-L6-v2"
    
    # 检查是否已存在
    if os.path.exists(local_path):
        print(f"✓ Embedding 模型已存在于: {local_path}")
        print(f"  大小: {get_directory_size(local_path) / (1024*1024):.2f} MB")
        return True
    
    try:
        print(f"正在下载 Embedding 模型: {model_name}")
        print(f"保存到: {local_path}")
        print("这可能需要几分钟时间，请耐心等待...")
        
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(model_name)
        model.save(local_path)
        
        print(f"✓ Embedding 模型下载成功！")
        print(f"  位置: {os.path.abspath(local_path)}")
        print(f"  大小: {get_directory_size(local_path) / (1024*1024):.2f} MB")
        return True
        
    except Exception as e:
        print(f"✗ Embedding 模型下载失败: {e}")
        return False


def download_reranker_model():
    """下载 Reranker 模型"""
    print("\n" + "=" * 80)
    print("2. 下载 Reranker 模型")
    print("=" * 80)
    
    model_name = "BAAI/bge-reranker-base"
    local_path = "./models/bge-reranker-base"
    
    # 检查是否已存在
    if os.path.exists(local_path):
        print(f"✓ Reranker 模型已存在于: {local_path}")
        print(f"  大小: {get_directory_size(local_path) / (1024*1024):.2f} MB")
        return True
    
    try:
        print(f"正在下载 Reranker 模型: {model_name}")
        print(f"保存到: {local_path}")
        print("这可能需要几分钟时间，请耐心等待...")
        
        # 设置 HuggingFace 镜像
        os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
        
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        
        # 下载模型
        print("  - 下载模型权重...")
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        # 下载分词器
        print("  - 下载分词器...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # 保存到本地
        print("  - 保存到本地...")
        model.save_pretrained(local_path)
        tokenizer.save_pretrained(local_path)
        
        print(f"✓ Reranker 模型下载成功！")
        print(f"  位置: {os.path.abspath(local_path)}")
        print(f"  大小: {get_directory_size(local_path) / (1024*1024):.2f} MB")
        return True
        
    except Exception as e:
        print(f"✗ Reranker 模型下载失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_directory_size(path):
    """计算目录大小"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def update_config_files():
    """更新配置文件以使用本地模型"""
    print("\n" + "=" * 80)
    print("3. 更新配置文件")
    print("=" * 80)
    
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print(f"⚠ .env 文件不存在，跳过更新")
        return
    
    # 读取现有内容
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新 EMBEDDING_MODEL 配置
    if './models/all-MiniLM-L6-v2' in content:
        print("✓ Embedding 模型配置已正确指向本地路径")
    else:
        print("⚠ 请手动更新 .env 文件中的 EMBEDDING_MODEL 为 ./models/all-MiniLM-L6-v2")
    
    # 提示用户添加 RERANKER_MODEL 配置
    if 'RERANKER_MODEL' not in content:
        print("\n请在 .env 文件中添加以下配置：")
        print("RERANKER_MODEL=./models/bge-reranker-base")


def verify_models():
    """验证模型完整性"""
    print("\n" + "=" * 80)
    print("4. 验证模型完整性")
    print("=" * 80)
    
    models_ok = True
    
    # 验证 Embedding 模型
    embedding_path = "./models/all-MiniLM-L6-v2"
    if os.path.exists(embedding_path):
        required_files = ['config.json', 'model.safetensors', 'tokenizer.json']
        missing = [f for f in required_files if not os.path.exists(os.path.join(embedding_path, f))]
        if missing:
            print(f"✗ Embedding 模型缺少文件: {missing}")
            models_ok = False
        else:
            print(f"✓ Embedding 模型完整")
    else:
        print(f"✗ Embedding 模型不存在: {embedding_path}")
        models_ok = False
    
    # 验证 Reranker 模型
    reranker_path = "./models/bge-reranker-base"
    if os.path.exists(reranker_path):
        required_files = ['config.json', 'pytorch_model.bin', 'tokenizer.json']
        missing = [f for f in required_files if not os.path.exists(os.path.join(reranker_path, f))]
        if missing:
            print(f"✗ Reranker 模型缺少文件: {missing}")
            models_ok = False
        else:
            print(f"✓ Reranker 模型完整")
    else:
        print(f"⚠ Reranker 模型未下载（可选）")
    
    return models_ok


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("KRET-RAG 模型下载工具")
    print("=" * 80)
    print("\n此脚本将下载所有必需的模型到本地，避免每次启动都联网")
    print("预计总大小：约 500MB")
    print("\n提示：首次下载可能需要较长时间，请耐心等待")
    
    # 创建 models 目录
    os.makedirs("./models", exist_ok=True)
    
    # 下载模型
    embedding_ok = download_embedding_model()
    reranker_ok = download_reranker_model()
    
    # 更新配置
    update_config_files()
    
    # 验证
    models_ok = verify_models()
    
    # 总结
    print("\n" + "=" * 80)
    print("下载完成总结")
    print("=" * 80)
    
    if models_ok:
        print("\n✓ 所有模型已成功下载到本地！")
        print("\n下一步操作：")
        print("1. 确认 .env 文件中配置了正确的本地路径")
        print("2. 重启服务以使用本地模型")
        print("3. 服务启动后将不再需要联网下载模型")
    else:
        print("\n⚠ 部分模型下载失败或验证不通过")
        print("请检查错误信息并重新运行脚本")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

"""
修复 ChromaDB Collection - 使用余弦相似度

问题：当前 collection 使用 L2 距离，导致相似度为负数
解决：删除旧 collection，创建新的使用余弦相似度的 collection
"""
import chromadb
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings


def fix_chromadb_collection():
    """修复 ChromaDB collection 的距离度量"""
    
    print("\n" + "=" * 80)
    print("ChromaDB Collection 修复工具")
    print("=" * 80)
    
    # 1. 连接 ChromaDB
    print(f"\n[步骤1] 连接 ChromaDB: {settings.CHROMA_HOST}")
    client = chromadb.PersistentClient(path=settings.CHROMA_HOST)
    
    # 2. 检查现有 collection
    print(f"\n[步骤2] 检查现有 collection...")
    try:
        existing_collection = client.get_collection(name=settings.CHROMA_COLLECTION_NAME)
        print(f"  - 找到现有 collection: {settings.CHROMA_COLLECTION_NAME}")
        
        # 获取文档数量
        count = existing_collection.count()
        print(f"  - 文档数量: {count}")
        
        if count == 0:
            print(f"\n  [INFO] Collection 为空，可以直接删除重建")
        else:
            print(f"\n  [WARN] Collection 中有 {count} 条数据！")
            print(f"  继续操作将删除所有现有数据！")
            
            confirm = input(f"\n  是否继续？(输入 'yes' 确认): ")
            if confirm.lower() != 'yes':
                print("\n[取消] 操作已取消")
                return
        
        # 3. 删除旧 collection
        print(f"\n[步骤3] 删除旧 collection...")
        client.delete_collection(name=settings.CHROMA_COLLECTION_NAME)
        print(f"  [OK] 已删除 collection: {settings.CHROMA_COLLECTION_NAME}")
        
    except Exception as e:
        print(f"  [INFO] 未找到现有 collection: {e}")
    
    # 4. 创建新 collection（使用余弦相似度）
    print(f"\n[步骤4] 创建新 collection（余弦相似度）...")
    new_collection = client.create_collection(
        name=settings.CHROMA_COLLECTION_NAME,
        metadata={
            "description": "RAG文档向量集合",
            "hnsw:space": "cosine"  # 使用余弦相似度
        }
    )
    print(f"  [OK] 已创建新 collection: {settings.CHROMA_COLLECTION_NAME}")
    print(f"  - 距离度量: cosine (余弦相似度)")
    print(f"  - 相似度范围: [-1, 1]")
    
    # 5. 验证
    print(f"\n[步骤5] 验证新 collection...")
    verify_collection = client.get_collection(name=settings.CHROMA_COLLECTION_NAME)
    print(f"  [OK] Collection 验证成功")
    print(f"  - 名称: {verify_collection.name}")
    print(f"  - 文档数量: {verify_collection.count()}")
    
    print("\n" + "=" * 80)
    print("修复完成！")
    print("=" * 80)
    print("\n下一步操作：")
    print("1. 重启 rag-scheduler 服务")
    print("2. 重新上传文档以填充向量数据库")
    print("3. 测试查询功能，确认相似度为正数")


if __name__ == "__main__":
    try:
        fix_chromadb_collection()
    except KeyboardInterrupt:
        print("\n\n[取消] 用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] 操作失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

"""
调试向量检索 - 检查Embedding模型和ChromaDB查询
"""
import asyncio
import sys
import os

# 设置控制台编码为 UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from app.services.vector_service import vector_store_service


async def debug_vector_search():
    """详细调试向量检索的每个步骤"""
    
    print("\n" + "=" * 80)
    print("向量检索深度调试")
    print("=" * 80)
    
    # 1. 初始化向量服务
    print("\n[步骤1] 初始化向量服务...")
    await vector_store_service.initialize()
    print("[OK] 向量服务初始化成功")
    
    # 2. 检查 ChromaDB 连接
    print(f"\n[步骤2] 检查 ChromaDB 状态:")
    print(f"  - Collection: {vector_store_service.collection.name if vector_store_service.collection else 'None'}")
    
    if vector_store_service.collection:
        count = vector_store_service.collection.count()
        print(f"  - 文档数量: {count}")
        
        # 获取一个示例
        sample = vector_store_service.collection.get(limit=1)
        if sample['ids']:
            print(f"  - 示例ID: {sample['ids'][0]}")
            print(f"  - 示例内容: {sample['documents'][0][:100]}...")
    
    # 3. 测试 Embedding 生成
    print(f"\n[步骤3] 测试 Embedding 生成:")
    test_query = "员工管理"
    print(f"  - 查询文本: '{test_query}'")
    
    try:
        embedding = vector_store_service.generate_embedding(test_query)
        print(f"  [OK] Embedding 生成成功")
        print(f"  - 维度: {len(embedding)}")
        print(f"  - 前5个值: {embedding[:5]}")
    except Exception as e:
        print(f"  [ERROR] Embedding 生成失败: {e}")
        return
    
    # 4. 直接调用 ChromaDB query
    print(f"\n[步骤4] 直接调用 ChromaDB query:")
    try:
        results = vector_store_service.collection.query(
            query_embeddings=[embedding],
            n_results=5,
            include=["documents", "distances", "metadatas"]
        )
        
        print(f"  - 返回的IDs数量: {len(results['ids'][0]) if results['ids'] else 0}")
        
        if results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                distance = results['distances'][0][i]
                similarity = 1.0 - distance
                content = results['documents'][0][i][:80]
                print(f"  [{i+1}] ID: {doc_id[:20]}..., 距离: {distance:.4f}, 相似度: {similarity:.4f}")
                print(f"      内容: {content}...")
        else:
            print(f"  [WARN] ChromaDB 返回空结果")
            
    except Exception as e:
        print(f"  [ERROR] ChromaDB query 失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. 测试不同的查询
    print(f"\n[步骤5] 测试多个查询:")
    test_queries = ["系统", "管理", "文档", "RAG"]
    
    for query in test_queries:
        try:
            emb = vector_store_service.generate_embedding(query)
            res = vector_store_service.collection.query(
                query_embeddings=[emb],
                n_results=3,
                include=["documents", "distances"]
            )
            
            if res['ids'] and res['ids'][0]:
                best_score = 1.0 - res['distances'][0][0]
                print(f"  [OK] '{query}': 最佳相似度 {best_score:.4f}")
            else:
                print(f"  [ERROR] '{query}': 无结果")
                
        except Exception as e:
            print(f"  [ERROR] '{query}': 错误 - {e}")
    
    print("\n" + "=" * 80)
    print("调试完成！")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(debug_vector_search())

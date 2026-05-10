"""
测试实际查询 - 检查相似度分数和编码
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.services.vector_service import vector_store_service


async def test_actual_query():
    """测试实际查询"""
    
    print("\n" + "=" * 80)
    print("实际查询测试")
    print("=" * 80)
    
    # 初始化
    await vector_store_service.initialize()
    
    # 测试查询
    query = "一套基于微服务架构的RAG"
    print(f"\n查询文本: '{query}'")
    print(f"查询长度: {len(query)} 字符")
    print(f"查询编码: {type(query)}")
    
    # 生成查询向量
    print("\n[步骤1] 生成查询向量...")
    query_embedding = vector_store_service.generate_embedding(query)
    print(f"  向量维度: {len(query_embedding)}")
    print(f"  前5个值: {query_embedding[:5]}")
    
    # 直接查询 ChromaDB（不使用阈值过滤）
    print("\n[步骤2] 直接查询 ChromaDB（无阈值过滤）...")
    results = vector_store_service.collection.query(
        query_embeddings=[query_embedding],
        n_results=10,
        include=["documents", "distances", "metadatas"]
    )
    
    if results['ids'] and results['ids'][0]:
        print(f"  返回结果数量: {len(results['ids'][0])}")
        print(f"\n  详细结果:")
        for i, (doc_id, distance, doc) in enumerate(zip(
            results['ids'][0], 
            results['distances'][0], 
            results['documents'][0]
        )):
            similarity = 1.0 - distance
            print(f"\n  [{i+1}] ID: {doc_id[:30]}...")
            print(f"      距离: {distance:.6f}")
            print(f"      相似度: {similarity:.6f}")
            print(f"      内容: {doc[:100]}...")
            
            # 检查是否通过阈值
            threshold = 0.7
            if similarity >= threshold:
                print(f"      ✅ 通过阈值 {threshold}")
            else:
                print(f"      ❌ 未通过阈值 {threshold} (差值: {threshold - similarity:.6f})")
    else:
        print("  ❌ 没有返回任何结果")
    
    # 测试不同的阈值
    print("\n[步骤3] 测试不同阈值下的结果数量...")
    thresholds = [0.1, 0.3, 0.5, 0.7, 0.9]
    
    for threshold in thresholds:
        count = sum(1 for d in results['distances'][0] if (1.0 - d) >= threshold)
        print(f"  阈值 {threshold}: {count} 个结果")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_actual_query())

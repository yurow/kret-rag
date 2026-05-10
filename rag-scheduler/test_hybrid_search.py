"""
测试混合检索功能（BM25 + 向量 + Rerank）
"""
import httpx
import asyncio


async def test_vector_only():
    """测试纯向量检索"""
    print("=" * 80)
    print("测试 1: 纯向量检索（不使用 BM25 和 Rerank）")
    print("=" * 80)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/query/search",
            json={
                "query": "什么是机器学习？",
                "top_k": 5,
                "score_threshold": 0.5,
                "use_hybrid": False,
                "use_rerank": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 搜索成功！")
            print(f"找到 {result['total']} 个相关结果\n")
            
            for i, item in enumerate(result['results'], 1):
                print(f"--- 结果 {i} ---")
                print(f"相似度: {item['similarity_score']:.4f}")
                print(f"内容预览: {item['content'][:100]}...")
                print()
        else:
            print(f"\n❌ 搜索失败: {response.status_code}")
            print(response.text)


async def test_hybrid_search():
    """测试混合检索（BM25 + 向量）"""
    print("\n" + "=" * 80)
    print("测试 2: 混合检索（BM25 + 向量，不使用 Rerank）")
    print("=" * 80)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/query/search",
            json={
                "query": "深度学习与神经网络的区别",
                "top_k": 5,
                "score_threshold": 0.5,
                "use_hybrid": True,
                "use_rerank": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 混合搜索成功！")
            print(f"找到 {result['total']} 个相关结果\n")
            
            for i, item in enumerate(result['results'], 1):
                print(f"--- 结果 {i} ---")
                print(f"相似度: {item['similarity_score']:.4f}")
                print(f"内容预览: {item['content'][:100]}...")
                print()
        else:
            print(f"\n❌ 搜索失败: {response.status_code}")
            print(response.text)


async def test_hybrid_with_rerank():
    """测试完整混合检索（BM25 + 向量 + Rerank）"""
    print("\n" + "=" * 80)
    print("测试 3: 完整混合检索（BM25 + 向量 + Rerank）⭐")
    print("=" * 80)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/query/search",
            json={
                "query": "Transformer 模型的工作原理",
                "top_k": 5,
                "score_threshold": 0.5,
                "use_hybrid": True,
                "use_rerank": True
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 完整混合搜索成功！")
            print(f"找到 {result['total']} 个相关结果\n")
            
            for i, item in enumerate(result['results'], 1):
                print(f"--- 结果 {i} ---")
                print(f"重排分数: {item['similarity_score']:.4f}")
                print(f"内容预览: {item['content'][:100]}...")
                print()
        else:
            print(f"\n❌ 搜索失败: {response.status_code}")
            print(response.text)


async def test_full_rag_query():
    """测试完整 RAG 查询（使用混合检索）"""
    print("\n" + "=" * 80)
    print("测试 4: 完整 RAG 查询（混合检索 + 上下文构建）")
    print("=" * 80)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/query/",
            json={
                "query": "什么是人工智能？",
                "top_k": 5,
                "score_threshold": 0.7,
                "use_hybrid": True,
                "use_rerank": True
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ RAG 查询成功！")
            print(f"找到 {result['total']} 个相关结果")
            print(f"查询耗时: {result['query_time']:.3f}秒\n")
            
            # 显示上下文
            if result.get('context'):
                print("构建的上下文:")
                print("-" * 80)
                print(result['context'][:500] + "...")
                print("-" * 80)
                print()
            
            # 显示结果
            for i, item in enumerate(result['results'], 1):
                print(f"--- 结果 {i} ---")
                print(f"分数: {item['score']:.4f}")
                print(f"内容: {item['content'][:150]}...")
                print()
        else:
            print(f"\n❌ 查询失败: {response.status_code}")
            print(response.text)


async def compare_search_methods():
    """对比不同检索方法的效果"""
    print("\n" + "=" * 80)
    print("测试 5: 对比不同检索方法的效果")
    print("=" * 80)
    
    query = "机器学习的优势是什么？"
    
    methods = [
        ("纯向量检索", {"use_hybrid": False, "use_rerank": False}),
        ("BM25 + 向量", {"use_hybrid": True, "use_rerank": False}),
        ("BM25 + 向量 + Rerank ⭐", {"use_hybrid": True, "use_rerank": True}),
    ]
    
    async with httpx.AsyncClient() as client:
        for method_name, params in methods:
            print(f"\n{'='*60}")
            print(f"方法: {method_name}")
            print(f"{'='*60}")
            
            response = await client.post(
                "http://localhost:8000/query/search",
                json={
                    "query": query,
                    "top_k": 3,
                    "score_threshold": 0.5,
                    **params
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"找到 {result['total']} 个结果")
                
                if result['results']:
                    print(f"Top-1 分数: {result['results'][0]['similarity_score']:.4f}")
                    print(f"Top-1 内容: {result['results'][0]['content'][:100]}...")
            else:
                print(f"❌ 失败: {response.status_code}")


async def main():
    """运行所有测试"""
    print("\n🚀 开始混合检索功能测试\n")
    
    try:
        # 测试 1: 纯向量检索
        await test_vector_only()
        
        # 测试 2: 混合检索（无 Rerank）
        await test_hybrid_search()
        
        # 测试 3: 完整混合检索（带 Rerank）
        await test_hybrid_with_rerank()
        
        # 测试 4: 完整 RAG 查询
        await test_full_rag_query()
        
        # 测试 5: 对比不同方法
        await compare_search_methods()
        
        print("\n" + "=" * 80)
        print("✅ 所有测试完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

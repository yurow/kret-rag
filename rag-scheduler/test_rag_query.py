"""
测试 RAG 查询功能
"""
import httpx
import asyncio


async def test_rag_search():
    """测试向量搜索功能"""
    print("=" * 60)
    print("测试 1: 向量搜索（不生成回答）")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/query/search",
            json={
                "query": "什么是机器学习？",
                "top_k": 3,
                "score_threshold": 0.5
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 搜索成功！")
            print(f"找到 {result['total']} 个相关结果\n")
            
            for i, item in enumerate(result['results'], 1):
                print(f"--- 结果 {i} ---")
                print(f"相似度: {item['similarity_score']:.4f}")
                print(f"文档ID: {item['document_id']}")
                print(f"内容预览: {item['content'][:100]}...")
                print()
        else:
            print(f"\n❌ 搜索失败: {response.status_code}")
            print(response.text)


async def test_rag_query():
    """测试完整查询功能"""
    print("\n" + "=" * 60)
    print("测试 2: 完整查询（检索 + 上下文构建）")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/query/",
            json={
                "query": "什么是机器学习？",
                "top_k": 5,
                "score_threshold": 0.7
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 查询成功！")
            print(f"找到 {result['total']} 个相关结果")
            print(f"查询耗时: {result['query_time']:.3f}秒\n")
            
            # 显示上下文
            if result.get('context'):
                print("构建的上下文:")
                print("-" * 60)
                print(result['context'][:500] + "...")
                print("-" * 60)
                print()
            
            # 显示结果
            for i, item in enumerate(result['results'], 1):
                print(f"--- 结果 {i} ---")
                print(f"相似度: {item['score']:.4f}")
                print(f"内容: {item['content'][:150]}...")
                print()
        else:
            print(f"\n❌ 查询失败: {response.status_code}")
            print(response.text)


async def test_rag_generate():
    """测试完整RAG生成回答功能"""
    print("\n" + "=" * 60)
    print("测试 3: RAG生成回答（需要LLM服务）")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "http://localhost:8000/query/generate",
            json={
                "query": "什么是机器学习？",
                "top_k": 5,
                "score_threshold": 0.7
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 回答生成成功！")
            print(f"查询耗时: {result['query_time']:.3f}秒\n")
            
            print("生成的回答:")
            print("-" * 60)
            print(result['answer'])
            print("-" * 60)
            print()
            
            print(f"参考来源 ({len(result['sources'])} 个):")
            for i, source in enumerate(result['sources'], 1):
                print(f"{i}. [相似度: {source['score']:.4f}] {source['content']}")
        else:
            print(f"\n❌ 回答生成失败: {response.status_code}")
            print(response.text)


async def main():
    """运行所有测试"""
    print("\n🚀 开始 RAG 功能测试\n")
    
    try:
        # 测试 1: 向量搜索
        await test_rag_search()
        
        # 测试 2: 完整查询
        await test_rag_query()
        
        # 测试 3: 生成回答（可选，需要LLM服务）
        # await test_rag_generate()
        
        print("\n" + "=" * 60)
        print("✅ 测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

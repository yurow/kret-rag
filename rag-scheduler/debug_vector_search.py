"""
测试向量检索功能 - 调试为什么返回空结果
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from app.services.vector_service import vector_store_service


async def test_vector_search():
    """测试不同参数下的向量检索效果"""
    
    print("\n" + "=" * 80)
    print("向量检索调试工具")
    print("=" * 80)
    
    # 初始化向量服务
    print("\n正在初始化向量服务...")
    await vector_store_service.initialize()
    print("✅ 向量服务初始化成功\n")
    
    # 测试查询
    test_queries = [
        "员工管理",
        "任务调度",
        "RAG系统",
        "文档处理"
    ]
    
    for query in test_queries:
        print(f"\n{'=' * 80}")
        print(f"测试查询: '{query}'")
        print(f"{'=' * 80}")
        
        # 测试不同的 score_threshold
        thresholds = [0.3, 0.5, 0.7, 0.9]
        
        for threshold in thresholds:
            try:
                results = await vector_store_service.similarity_search(
                    query=query,
                    top_k=5,
                    score_threshold=threshold,
                    use_hybrid=False  # 先测试纯向量检索
                )
                
                print(f"\n  阈值 {threshold}: 找到 {len(results)} 个结果")
                if results:
                    for i, r in enumerate(results[:2]):  # 只显示前2个
                        print(f"    [{i+1}] 分数: {r.similarity_score:.4f}, 内容: {r.content[:50]}...")
                
            except Exception as e:
                print(f"  ❌ 错误: {e}")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
    print("\n💡 建议：")
    print("  - 如果阈值0.7时结果为空，尝试降低到0.5或0.3")
    print("  - 检查查询是否与文档内容相关")
    print("  - 确认 ChromaDB 中有数据（运行 python check_chromadb.py）")


if __name__ == "__main__":
    asyncio.run(test_vector_search())

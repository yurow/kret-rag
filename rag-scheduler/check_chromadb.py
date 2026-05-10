"""
检查 ChromaDB 中的数据
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

async def check_chromadb():
    """检查 ChromaDB 数据"""
    print("=" * 80)
    print("ChromaDB 数据检查工具")
    print("=" * 80)
    
    from app.services.vector_service import vector_store_service
    
    try:
        # 初始化向量服务
        print("\n正在初始化向量服务...")
        await vector_store_service.initialize()
        print("✅ 向量服务初始化成功")
        
        # 获取 collection
        collection = vector_store_service.collection
        if not collection:
            print("❌ Collection 未初始化")
            return
        
        # 统计文档数量
        count = collection.count()
        print(f"\n📊 ChromaDB 中的文档总数: {count}")
        
        if count == 0:
            print("\n⚠️  ChromaDB 中没有数据！")
            print("\n可能的原因：")
            print("1. 还没有上传任何文档")
            print("2. 文档上传时向量化任务失败")
            print("3. ChromaDB 数据被清空或删除")
            print("\n建议操作：")
            print("1. 访问 http://localhost:8000/ 上传一个测试文档")
            print("2. 观察日志中是否有向量化成功的消息")
            print("3. 再次运行此脚本检查数据")
        else:
            print(f"\n✅ ChromaDB 中有 {count} 条记录")
            
            # 显示一些示例
            print("\n示例数据（前5条）:")
            results = collection.peek(limit=5)
            
            for i, (doc_id, doc, meta) in enumerate(zip(
                results['ids'],
                results['documents'],
                results['metadatas']
            ), 1):
                print(f"\n  {i}. ID: {doc_id}")
                print(f"     内容: {doc[:100]}..." if len(doc) > 100 else f"     内容: {doc}")
                print(f"     元数据: {meta}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ 检查失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_chromadb())

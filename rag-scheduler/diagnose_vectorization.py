"""
诊断脚本 - 检查向量化任务状态和ChromaDB数据
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

async def diagnose():
    """诊断函数"""
    print("=" * 80)
    print("KRET-RAG 向量化诊断工具")
    print("=" * 80)
    
    # 1. 检查后台任务状态
    print("\n【1】检查后台任务状态...")
    from app.services.background_task_service import background_task_service
    
    tasks = background_task_service.list_tasks()
    if tasks:
        print(f"找到 {len(tasks)} 个任务:")
        for task in tasks[:5]:  # 只显示最近5个
            print(f"  - Task ID: {task.task_id}")
            print(f"    状态: {task.status}")
            print(f"    进度: {task.progress}%")
            print(f"    消息: {task.message}")
            if task.error:
                print(f"    错误: {task.error}")
            print()
    else:
        print("  ⚠️ 没有找到任何任务记录")
    
    # 2. 检查ChromaDB数据
    print("\n【2】检查ChromaDB向量数据库...")
    from app.services.vector_service import vector_store_service
    
    try:
        # 初始化向量服务
        await vector_store_service.initialize()
        
        # 获取collection中的文档数量
        collection = vector_store_service.collection
        if collection:
            count = collection.count()
            print(f"  ✅ ChromaDB Collection 中存在 {count} 条记录")
            
            if count > 0:
                # 显示一些示例
                results = collection.peek(limit=3)
                print(f"\n  示例数据（前3条）:")
                for i, (doc_id, doc, meta) in enumerate(zip(
                    results['ids'][0] if isinstance(results['ids'], list) and len(results['ids']) > 0 else [],
                    results['documents'][0] if isinstance(results['documents'], list) and len(results['documents']) > 0 else [],
                    results['metadatas'][0] if isinstance(results['metadatas'], list) and len(results['metadatas']) > 0 else []
                ), 1):
                    print(f"    {i}. ID: {doc_id}")
                    print(f"       内容: {doc[:100]}..." if len(doc) > 100 else f"       内容: {doc}")
                    print(f"       元数据: {meta}")
        else:
            print("  ❌ ChromaDB Collection 未初始化")
            
    except Exception as e:
        print(f"  ❌ 检查ChromaDB失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 3. 检查数据库中的文档记录
    print("\n【3】检查SQLite数据库中的文档记录...")
    from app.db.database import db_manager
    from app.repositories.document_repository import DocumentRepository
    
    db_session = db_manager.SessionLocal()
    try:
        repo = DocumentRepository(db_session)
        documents = repo.list_documents(skip=0, limit=10)
        
        if documents:
            print(f"  ✅ 数据库中存在 {len(documents)} 个文档:")
            for doc in documents:
                print(f"    - ID: {doc.document_id}")
                print(f"      文件名: {doc.file_name}")
                print(f"      状态: {doc.status}")
                print(f"      文本长度: {doc.text_length}")
                print(f"      创建时间: {doc.created_at}")
                print()
        else:
            print("  ⚠️ 数据库中没有文档记录")
    finally:
        db_session.close()
    
    # 4. 建议的解决方案
    print("\n【4】问题诊断与建议:")
    print("=" * 80)
    
    if not tasks:
        print("⚠️ 问题1: 没有找到后台任务记录")
        print("   可能原因: 服务重启后任务状态丢失（内存存储）")
        print("   建议: 重新上传文件，或修改代码使用同步模式")
        print()
    
    print("💡 解决方案:")
    print("  方案1: 等待后台任务完成（如果任务还在运行）")
    print("  方案2: 修改 upload_document 方法，设置 use_async=False 使用同步模式")
    print("  方案3: 手动触发向量化任务")
    print()
    
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(diagnose())

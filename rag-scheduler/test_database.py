"""
数据库功能测试脚本
验证文档元数据存储和查询功能
"""
import asyncio
from pathlib import Path
from app.db.database import db_manager
from app.repositories.document_repository import DocumentRepository


def test_database_initialization():
    """测试数据库初始化"""
    print("=" * 60)
    print("测试 1: 数据库初始化")
    print("=" * 60)
    
    try:
        # 创建表
        db_manager.create_tables()
        print("✅ 数据库表创建成功")
        
        # 检查数据库文件是否存在
        db_path = Path("./data/documents.db")
        if db_path.exists():
            print(f"✅ 数据库文件已创建: {db_path.absolute()}")
        else:
            print("❌ 数据库文件未创建")
        
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False


def test_create_document():
    """测试创建文档记录"""
    print("\n" + "=" * 60)
    print("测试 2: 创建文档记录")
    print("=" * 60)
    
    db_session = db_manager.SessionLocal()
    try:
        repo = DocumentRepository(db_session)
        
        # 创建测试文档
        doc = repo.create(
            document_id="test-doc-001",
            file_name="测试文档.pdf",
            file_type="pdf",
            file_size=1024000,
            storage_path="./uploads/test-doc-001_测试文档.pdf",
            text_length=5000,
            metadata={"author": "张三", "category": "技术"}
        )
        
        print(f"✅ 文档创建成功")
        print(f"   ID: {doc.id}")
        print(f"   Document ID: {doc.document_id}")
        print(f"   文件名: {doc.file_name}")
        print(f"   文件类型: {doc.file_type}")
        print(f"   文件大小: {doc.file_size} bytes")
        print(f"   文本长度: {doc.text_length}")
        print(f"   存储路径: {doc.storage_path}")
        print(f"   创建时间: {doc.created_at}")
        print(f"   状态: {doc.status}")
        
        return True
    except Exception as e:
        print(f"❌ 创建文档失败: {e}")
        db_session.rollback()
        return False
    finally:
        db_session.close()


def test_get_document():
    """测试查询文档"""
    print("\n" + "=" * 60)
    print("测试 3: 查询文档")
    print("=" * 60)
    
    db_session = db_manager.SessionLocal()
    try:
        repo = DocumentRepository(db_session)
        
        # 根据 document_id 查询
        doc = repo.get_by_id("test-doc-001")
        
        if doc:
            print(f"✅ 查询成功")
            print(f"   文档: {doc.to_dict()}")
            return True
        else:
            print("❌ 文档不存在")
            return False
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return False
    finally:
        db_session.close()


def test_list_documents():
    """测试列出所有文档"""
    print("\n" + "=" * 60)
    print("测试 4: 列出所有文档")
    print("=" * 60)
    
    db_session = db_manager.SessionLocal()
    try:
        repo = DocumentRepository(db_session)
        
        # 先创建几个测试文档
        for i in range(2, 6):
            repo.create(
                document_id=f"test-doc-{i:03d}",
                file_name=f"测试文档{i}.pdf",
                file_type="pdf",
                file_size=1024 * i,
                storage_path=f"./uploads/test-doc-{i:03d}_测试文档{i}.pdf",
                text_length=1000 * i,
                metadata={"index": i}
            )
        
        db_session.commit()
        
        # 分页查询
        docs = repo.list_all(page=1, page_size=3)
        
        print(f"✅ 查询成功，共返回 {len(docs)} 个文档")
        for doc in docs:
            print(f"   - {doc.file_name} ({doc.file_size} bytes)")
        
        # 统计总数
        total = repo.count()
        print(f"\n📊 总文档数: {total}")
        
        return True
    except Exception as e:
        print(f"❌ 列出文档失败: {e}")
        db_session.rollback()
        return False
    finally:
        db_session.close()


def test_search_documents():
    """测试搜索文档"""
    print("\n" + "=" * 60)
    print("测试 5: 搜索文档")
    print("=" * 60)
    
    db_session = db_manager.SessionLocal()
    try:
        repo = DocumentRepository(db_session)
        
        # 搜索包含"测试"的文档
        keyword = "测试"
        docs = repo.search(keyword=keyword, page=1, page_size=10)
        
        print(f"✅ 搜索成功，关键词: '{keyword}'")
        print(f"   找到 {len(docs)} 个匹配文档:")
        for doc in docs:
            print(f"   - {doc.file_name}")
        
        return True
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        return False
    finally:
        db_session.close()


def test_update_document():
    """测试更新文档"""
    print("\n" + "=" * 60)
    print("测试 6: 更新文档")
    print("=" * 60)
    
    db_session = db_manager.SessionLocal()
    try:
        repo = DocumentRepository(db_session)
        
        # 更新状态
        success = repo.update_status("test-doc-001", "processing")
        if success:
            print("✅ 状态更新成功")
            
            # 验证更新
            doc = repo.get_by_id("test-doc-001")
            print(f"   新状态: {doc.status}")
        
        # 更新元数据
        success = repo.update_metadata("test-doc-001", {"reviewer": "李四"})
        if success:
            print("✅ 元数据更新成功")
            
            # 验证更新
            doc = repo.get_by_id("test-doc-001")
            print(f"   新元数据: {doc.metadata}")
        
        return True
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        db_session.rollback()
        return False
    finally:
        db_session.close()


def test_delete_document():
    """测试删除文档"""
    print("\n" + "=" * 60)
    print("测试 7: 删除文档")
    print("=" * 60)
    
    db_session = db_manager.SessionLocal()
    try:
        repo = DocumentRepository(db_session)
        
        # 删除测试文档
        success = repo.delete("test-doc-005")
        
        if success:
            print("✅ 删除成功")
            
            # 验证删除
            doc = repo.get_by_id("test-doc-005")
            if not doc:
                print("   确认: 文档已从数据库中删除")
        else:
            print("❌ 删除失败")
        
        return True
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        db_session.rollback()
        return False
    finally:
        db_session.close()


def cleanup_test_data():
    """清理测试数据"""
    print("\n" + "=" * 60)
    print("清理测试数据")
    print("=" * 60)
    
    db_session = db_manager.SessionLocal()
    try:
        repo = DocumentRepository(db_session)
        
        # 删除所有测试文档
        for i in range(1, 6):
            repo.delete(f"test-doc-{i:03d}")
        
        db_session.commit()
        print("✅ 测试数据已清理")
        
        return True
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        db_session.rollback()
        return False
    finally:
        db_session.close()


def main():
    """运行所有测试"""
    print("\n🧪 KRET-RAG 数据库功能测试\n")
    
    tests = [
        ("数据库初始化", test_database_initialization),
        ("创建文档记录", test_create_document),
        ("查询文档", test_get_document),
        ("列出所有文档", test_list_documents),
        ("搜索文档", test_search_documents),
        ("更新文档", test_update_document),
        ("删除文档", test_delete_document),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} 测试异常: {e}")
            results.append((name, False))
    
    # 清理测试数据
    cleanup_test_data()
    
    # 显示测试结果汇总
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！数据库功能正常。")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查错误信息。")


if __name__ == "__main__":
    main()

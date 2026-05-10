"""
依赖验证脚本 - 检查所有必需的包是否可以正常导入
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import(package_name, display_name=None):
    """测试导入一个包"""
    name = display_name or package_name
    try:
        __import__(package_name)
        print(f"✅ {name}")
        return True
    except ImportError as e:
        print(f"❌ {name}: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("KRET-RAG Scheduler 依赖验证")
    print("=" * 60)
    print()
    
    # 核心框架
    print("📦 核心框架:")
    test_import("fastapi", "FastAPI")
    test_import("uvicorn", "Uvicorn")
    test_import("pydantic", "Pydantic")
    print()
    
    # 数据库
    print("🗄️  数据库:")
    test_import("sqlalchemy", "SQLAlchemy")
    test_import("psycopg2", "PostgreSQL驱动")
    print()
    
    # 向量数据库和嵌入
    print("🧠 向量数据库和嵌入:")
    test_import("chromadb", "ChromaDB")
    test_import("sentence_transformers", "Sentence Transformers")
    test_import("transformers", "Transformers")
    print()
    
    # 文档处理
    print("📄 文档处理:")
    test_import("pypdf", "PyPDF")
    test_import("docx", "python-docx")
    test_import("openpyxl", "OpenPyXL")
    test_import("pptx", "python-pptx")
    test_import("bs4", "BeautifulSoup")
    print()
    
    # 其他依赖
    print("🔧 其他依赖:")
    test_import("numpy", "NumPy")
    test_import("redis", "Redis")
    test_import("httpx", "HTTPX")
    test_import("rank_bm25", "Rank-BM25")
    test_import("jieba", "Jieba分词")
    print()
    
    # 测试应用模块导入
    print("🚀 应用模块:")
    try:
        from app.main import app
        print("✅ 应用主模块 (app.main)")
    except Exception as e:
        print(f"❌ 应用主模块: {str(e)}")
    print()
    
    print("=" * 60)
    print("验证完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()

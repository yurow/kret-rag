"""
诊断 ChromaDB 路径问题 - 检查为什么服务说没有文档但实际有数据
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings


def diagnose_chromadb_path():
    """诊断 ChromaDB 路径配置"""
    
    print("\n" + "=" * 80)
    print("ChromaDB 路径诊断工具")
    print("=" * 80)
    
    # 1. 显示当前工作目录
    print(f"\n[1] 当前工作目录:")
    print(f"    {os.getcwd()}")
    
    # 2. 显示配置的 CHROMA_HOST
    print(f"\n[2] 配置的 CHROMA_HOST:")
    print(f"    {settings.CHROMA_HOST}")
    
    # 3. 计算绝对路径
    abs_path = os.path.abspath(settings.CHROMA_HOST)
    print(f"\n[3] 解析后的绝对路径:")
    print(f"    {abs_path}")
    
    # 4. 检查目录是否存在
    if os.path.exists(abs_path):
        print(f"\n[4] 目录状态: ✅ 存在")
        
        # 列出目录内容
        files = os.listdir(abs_path)
        print(f"    文件数量: {len(files)}")
        if files:
            print(f"    文件列表:")
            for f in files[:5]:  # 只显示前5个
                print(f"      - {f}")
    else:
        print(f"\n[4] 目录状态: ❌ 不存在")
        print(f"    这会导致创建新的空 ChromaDB！")
    
    # 5. 检查是否有其他 chromadb 目录
    print(f"\n[5] 搜索项目中的 chromadb 目录:")
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    for root, dirs, files in os.walk(project_root):
        if 'chromadb' in dirs:
            chroma_path = os.path.join(root, 'chromadb')
            rel_path = os.path.relpath(chroma_path, project_root)
            
            # 检查是否有数据
            try:
                import chromadb
                client = chromadb.PersistentClient(path=chroma_path)
                collections = client.list_collections()
                
                total_docs = 0
                for col in collections:
                    collection = client.get_collection(col.name)
                    count = collection.count()
                    total_docs += count
                
                print(f"    ✅ {rel_path}")
                print(f"       Collections: {len(collections)}")
                print(f"       总文档数: {total_docs}")
            except Exception as e:
                print(f"    ⚠️  {rel_path} (错误: {e})")
    
    # 6. 建议
    print(f"\n{'=' * 80}")
    print("诊断结论和建议:")
    print("=" * 80)
    
    if not os.path.exists(abs_path):
        print("\n❌ 问题：配置的 ChromaDB 路径不存在")
        print("\n解决方案：")
        print("  1. 确认 .env 文件中的 CHROMA_HOST 路径正确")
        print("  2. 如果使用相对路径，确保启动时工作目录正确")
        print("  3. 建议使用绝对路径避免歧义")
        print(f"\n当前配置: CHROMA_HOST={settings.CHROMA_HOST}")
        print(f"建议修改为: CHROMA_HOST={abs_path}")
    else:
        print("\n✅ ChromaDB 路径存在，但可能没有数据")
        print("\n请检查：")
        print("  1. 是否上传过文档")
        print("  2. 向量化是否成功完成")
        print("  3. 查看服务日志确认初始化过程")


if __name__ == "__main__":
    diagnose_chromadb_path()

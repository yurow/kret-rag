"""
数据库迁移脚本 - 添加 text_file_path 字段
"""
import sqlite3
from pathlib import Path
from app.core.config import settings

def migrate_add_text_file_path():
    """
    为 document_metadata 表添加 text_file_path 字段
    
    注意：SQLite 不支持直接 ALTER TABLE ADD COLUMN 到特定位置，
    但可以添加到末尾，这对于我们的需求足够了。
    """
    db_path = Path(settings.SQLITE_DATABASE_PATH)
    
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        print("将在首次运行时自动创建新表结构")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 检查 text_file_path 字段是否已存在
        cursor.execute("PRAGMA table_info(document_metadata)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "text_file_path" in columns:
            print("✅ text_file_path 字段已存在，无需迁移")
            conn.close()
            return True
        
        print("开始添加 text_file_path 字段...")
        
        # 添加新字段
        cursor.execute("""
            ALTER TABLE document_metadata 
            ADD COLUMN text_file_path VARCHAR(1000)
        """)
        
        conn.commit()
        print("✅ 成功添加 text_file_path 字段")
        
        # 验证
        cursor.execute("PRAGMA table_info(document_metadata)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"当前表字段: {', '.join(columns)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("数据库迁移：添加 text_file_path 字段")
    print("=" * 60)
    
    success = migrate_add_text_file_path()
    
    if success:
        print("\n✅ 迁移完成！")
    else:
        print("\n❌ 迁移失败，请检查错误信息")

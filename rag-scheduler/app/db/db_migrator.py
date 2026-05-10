"""
数据库迁移管理器
统一管理数据库 schema 变更
"""
import sqlite3
from pathlib import Path
from app.core.config import settings


class DatabaseMigrator:
    """数据库迁移管理器"""
    
    def __init__(self):
        self.db_path = Path(settings.SQLITE_DATABASE_PATH)
        self.migrations = [
            self._migration_001_add_text_file_path,
            # 未来可以添加更多迁移
            # self._migration_002_add_xxx_field,
        ]
    
    def _get_connection(self):
        """获取数据库连接"""
        if not self.db_path.exists():
            raise FileNotFoundError(f"数据库文件不存在: {self.db_path}")
        return sqlite3.connect(str(self.db_path))
    
    def _check_column_exists(self, cursor, table_name, column_name):
        """检查字段是否存在"""
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        return column_name in columns
    
    def _migration_001_add_text_file_path(self):
        """
        迁移 001: 为 document_metadata 表添加 text_file_path 字段
        
        版本: 0.0.1
        日期: 2026-05-10
        描述: 支持存储清洗后文本文件的路径
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查是否已存在
            if self._check_column_exists(cursor, "document_metadata", "text_file_path"):
                print("✅ [Migration 001] text_file_path 字段已存在，跳过")
                conn.close()
                return True
            
            print("🔄 [Migration 001] 添加 text_file_path 字段...")
            
            # 添加新字段
            cursor.execute("""
                ALTER TABLE document_metadata 
                ADD COLUMN text_file_path VARCHAR(1000)
            """)
            
            conn.commit()
            print("✅ [Migration 001] 成功添加 text_file_path 字段")
            
            conn.close()
            return True
            
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"❌ [Migration 001] 失败: {str(e)}")
            raise
    
    def run_migrations(self):
        """
        执行所有待执行的迁移
        
        Returns:
            bool: 是否所有迁移都成功
        """
        if not self.db_path.exists():
            print(f"⚠️  数据库文件不存在: {self.db_path}")
            print("将在首次运行时自动创建新表结构")
            return False
        
        print("=" * 60)
        print("开始执行数据库迁移")
        print("=" * 60)
        
        success_count = 0
        total_count = len(self.migrations)
        
        for migration in self.migrations:
            try:
                if migration():
                    success_count += 1
            except Exception as e:
                print(f"\n❌ 迁移中断: {str(e)}")
                print(f"已成功执行 {success_count}/{total_count} 个迁移")
                return False
        
        print("=" * 60)
        print(f"✅ 所有迁移完成！成功执行 {success_count}/{total_count} 个迁移")
        print("=" * 60)
        
        return True


def run_migrations():
    """便捷函数：执行所有迁移"""
    migrator = DatabaseMigrator()
    return migrator.run_migrations()


if __name__ == "__main__":
    run_migrations()

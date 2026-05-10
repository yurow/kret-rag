"""
依赖检查脚本
验证所有必需的Python库是否已安装
"""

def check_dependencies():
    """检查所有依赖"""
    dependencies = {
        'pypdf': 'PDF解析',
        'docx': 'Word文档处理',
        'pptx': 'PowerPoint处理',
        'openpyxl': 'Excel处理',
        'chardet': '编码检测',
        'pandas': '数据处理',
        'fastapi': 'Web框架',
        'uvicorn': 'ASGI服务器',
        'pydantic': '数据验证',
    }
    
    print("=" * 60)
    print("📦 KRET-RAG 依赖检查")
    print("=" * 60)
    print()
    
    installed = []
    missing = []
    
    for package, description in dependencies.items():
        try:
            module = __import__(package)
            version = getattr(module, '__version__', '未知')
            print(f"✅ {package:20s} - {description:15s} (v{version})")
            installed.append(package)
        except ImportError as e:
            print(f"❌ {package:20s} - {description:15s} (未安装)")
            missing.append(package)
    
    print()
    print("=" * 60)
    print(f"结果: {len(installed)} 个已安装, {len(missing)} 个缺失")
    print("=" * 60)
    
    if missing:
        print()
        print("⚠️  缺失的依赖:")
        for pkg in missing:
            print(f"   - {pkg}")
        print()
        print("💡 安装命令:")
        print(f"   pip install {' '.join(missing)}")
        return False
    else:
        print()
        print("✅ 所有依赖已正确安装！可以开始使用文档上传功能。")
        return True


if __name__ == "__main__":
    check_dependencies()

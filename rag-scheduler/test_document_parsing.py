"""
文档上传功能快速测试脚本
用于验证各种格式文档的解析功能
"""
import asyncio
from pathlib import Path
from app.services.document_service import document_service


async def test_text_extraction():
    """测试文本文件提取"""
    print("=" * 60)
    print("测试 1: 文本文件提取")
    print("=" * 60)
    
    # 创建测试文本文件
    test_file = Path("./test_sample.txt")
    test_content = """
    这是测试文本。
    
    包含多个段落和空行。
    
    特殊字符: @#$%^&*()
    中英文混合: Hello 世界
    
    页脚信息: Page 1 of 5
    水印: CONFIDENTIAL
    """
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        text = await document_service._extract_from_text(str(test_file))
        cleaned = document_service.clean_text(text)
        
        print(f"✅ 原始长度: {len(text)} 字符")
        print(f"✅ 清理后长度: {len(cleaned)} 字符")
        print(f"\n清理后的内容:\n{cleaned[:200]}...")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        test_file.unlink(missing_ok=True)


async def test_pdf_extraction():
    """测试 PDF 文件提取（如果存在）"""
    print("\n" + "=" * 60)
    print("测试 2: PDF 文件提取")
    print("=" * 60)
    
    # 查找 uploads 目录中的 PDF 文件
    upload_dir = Path("./uploads")
    pdf_files = list(upload_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("⚠️  未找到 PDF 文件，请先上传一个 PDF 文档")
        return
    
    pdf_file = pdf_files[0]
    print(f"测试文件: {pdf_file.name}")
    
    try:
        text = await document_service._extract_from_pdf(str(pdf_file))
        cleaned = document_service.clean_text(text)
        
        print(f"✅ 原始长度: {len(text)} 字符")
        print(f"✅ 清理后长度: {len(cleaned)} 字符")
        print(f"\n前 300 字符:\n{cleaned[:300]}...")
        
    except Exception as e:
        print(f"❌ 错误: {e}")


async def test_docx_extraction():
    """测试 Word 文件提取（如果存在）"""
    print("\n" + "=" * 60)
    print("测试 3: Word 文件提取")
    print("=" * 60)
    
    upload_dir = Path("./uploads")
    docx_files = list(upload_dir.glob("*.docx"))
    
    if not docx_files:
        print("⚠️  未找到 DOCX 文件，请先上传一个 Word 文档")
        return
    
    docx_file = docx_files[0]
    print(f"测试文件: {docx_file.name}")
    
    try:
        text = await document_service._extract_from_docx(str(docx_file))
        cleaned = document_service.clean_text(text)
        
        print(f"✅ 原始长度: {len(text)} 字符")
        print(f"✅ 清理后长度: {len(cleaned)} 字符")
        print(f"\n前 300 字符:\n{cleaned[:300]}...")
        
    except Exception as e:
        print(f"❌ 错误: {e}")


async def test_excel_extraction():
    """测试 Excel 文件提取（如果存在）"""
    print("\n" + "=" * 60)
    print("测试 4: Excel 文件提取")
    print("=" * 60)
    
    upload_dir = Path("./uploads")
    excel_files = list(upload_dir.glob("*.xlsx")) + list(upload_dir.glob("*.xls"))
    
    if not excel_files:
        print("⚠️  未找到 Excel 文件，请先上传一个 Excel 文档")
        return
    
    excel_file = excel_files[0]
    print(f"测试文件: {excel_file.name}")
    
    try:
        text = await document_service._extract_from_excel(str(excel_file))
        cleaned = document_service.clean_text(text)
        
        print(f"✅ 原始长度: {len(text)} 字符")
        print(f"✅ 清理后长度: {len(cleaned)} 字符")
        print(f"\n前 300 字符:\n{cleaned[:300]}...")
        
    except Exception as e:
        print(f"❌ 错误: {e}")


async def test_text_cleaning():
    """测试文本清理功能"""
    print("\n" + "=" * 60)
    print("测试 5: 文本清理功能")
    print("=" * 60)
    
    test_cases = [
        ("页眉页脚", "Header\nPage 1 of 10\nContent\nFooter"),
        ("水印", "DRAFT Content CONFIDENTIAL"),
        ("多余空白", "Hello     World\n\n\n\nTest"),
        ("乱码", "Hello\x00World\x01Test"),
        ("混合", "Header\nPage 1 of 5\nDRAFT Content   Here\n\n\n\nFooter"),
    ]
    
    for name, text in test_cases:
        cleaned = document_service.clean_text(text)
        print(f"{name}:")
        print(f"  原始: {repr(text)}")
        print(f"  清理: {repr(cleaned)}")
        print()


async def main():
    """运行所有测试"""
    print("\n🧪 KRET-RAG 文档解析功能测试\n")
    
    # 确保 uploads 目录存在
    Path("./uploads").mkdir(exist_ok=True)
    
    # 运行测试
    await test_text_extraction()
    await test_text_cleaning()
    await test_pdf_extraction()
    await test_docx_extraction()
    await test_excel_extraction()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    print("\n提示:")
    print("1. 要测试 PDF/Word/Excel，请先通过 upload_test.html 上传文件")
    print("2. 上传的文件会保存在 ./uploads 目录")
    print("3. 然后重新运行此测试脚本\n")


if __name__ == "__main__":
    asyncio.run(main())

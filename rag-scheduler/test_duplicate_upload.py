"""
测试文件上传去重功能
"""
import requests
import os

# API 基础 URL
BASE_URL = "http://localhost:8000"

def test_duplicate_upload():
    """测试重复文件上传"""
    
    # 准备测试文件
    test_file_path = "test_document.txt"
    
    # 创建测试文件
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("这是一个测试文档，用于验证去重功能。\n" * 10)
    
    try:
        # 第一次上传
        print("=" * 60)
        print("第一次上传文件...")
        print("=" * 60)
        
        with open(test_file_path, "rb") as f:
            files = {"file": (os.path.basename(test_file_path), f)}
            response = requests.post(f"{BASE_URL}/documents/upload", files=files)
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        first_doc_id = response.json()["document_id"]
        first_is_duplicate = response.json().get("is_duplicate", False)
        
        print(f"\n文档ID: {first_doc_id}")
        print(f"是否重复: {first_is_duplicate}")
        
        # 第二次上传（相同文件）
        print("\n" + "=" * 60)
        print("第二次上传相同文件（测试去重）...")
        print("=" * 60)
        
        with open(test_file_path, "rb") as f:
            files = {"file": (os.path.basename(test_file_path), f)}
            response = requests.post(f"{BASE_URL}/documents/upload", files=files)
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        second_doc_id = response.json()["document_id"]
        second_is_duplicate = response.json().get("is_duplicate", False)
        
        print(f"\n文档ID: {second_doc_id}")
        print(f"是否重复: {second_is_duplicate}")
        
        # 验证结果
        print("\n" + "=" * 60)
        print("验证结果:")
        print("=" * 60)
        print(f"第一次上传 - 文档ID: {first_doc_id}, 是否重复: {first_is_duplicate}")
        print(f"第二次上传 - 文档ID: {second_doc_id}, 是否重复: {second_is_duplicate}")
        
        if first_doc_id == second_doc_id and second_is_duplicate:
            print("\n✅ 去重功能正常工作！两次上传返回相同的文档ID，且第二次标记为重复。")
        else:
            print("\n❌ 去重功能异常！请检查实现。")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"\n已清理测试文件: {test_file_path}")


if __name__ == "__main__":
    print("开始测试文件上传去重功能...\n")
    test_duplicate_upload()

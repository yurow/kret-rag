# 🔧 依赖安装问题解决

## ❌ 问题描述

上传 Word 文档时出现错误：
```
Failed to process document: DOCX extraction failed: No module named 'docx'
```

## ✅ 已解决

### 原因
`python-docx` 库未安装，导致无法解析 Word 文档。

### 解决方案

已安装所有必需的依赖包：

```bash
cd g:\rag\kret-rag\rag-scheduler
pip install python-docx pypdf python-pptx openpyxl chardet pandas
```

### 已安装的依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| **python-docx** | 1.2.0 | Word 文档解析 (.docx) |
| **pypdf** | 6.11.0 | PDF 文档解析 |
| **python-pptx** | 1.0.2 | PowerPoint 解析 (.pptx) |
| **openpyxl** | 3.1.5 | Excel 解析 (.xlsx) |
| **chardet** | 7.4.3 | 文本编码检测 |
| **pandas** | 3.0.1 | 数据处理（Excel/CSV） |

---

## 🚀 现在可以做什么

### 1. 重启服务（重要！）

由于是新安装的依赖，**必须重启 uvicorn 服务**才能生效：

```bash
# 方法一：使用启动脚本
start-upload-test.bat

# 方法二：手动重启
# 在运行服务的终端按 Ctrl+C
# 然后重新运行
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 测试 Word 文档上传

重启后：
1. 访问 http://localhost:8000/
2. 上传 `.docx` 文件
3. 应该能成功解析！

### 3. 验证依赖

运行依赖检查脚本：
```bash
python check_dependencies.py
```

应该看到：
```
✅ 所有依赖已正确安装！可以开始使用文档上传功能。
```

---

## 📋 支持的文档格式

现在完全支持以下格式：

- ✅ **PDF** (.pdf) - 使用 pypdf
- ✅ **Word** (.docx, .doc) - 使用 python-docx
- ✅ **PowerPoint** (.pptx, .ppt) - 使用 python-pptx
- ✅ **Excel** (.xlsx, .xls, .csv) - 使用 openpyxl + pandas
- ✅ **文本** (.txt, .md) - 使用 chardet 编码检测

---

## ⚠️ 注意事项

### 1. 必须重启服务

安装新依赖后，**Python 进程需要重启**才能加载新模块。

**症状**: 仍然报错 `No module named 'xxx'`  
**解决**: 重启 uvicorn 服务

### 2. 虚拟环境

如果你使用虚拟环境，确保在正确的环境中安装：

```bash
# 激活虚拟环境（如果有）
.\venv\Scripts\activate

# 然后安装依赖
pip install -r requirements.txt
```

### 3. 依赖冲突

如果遇到问题，可以尝试重新安装：

```bash
# 卸载旧版本
pip uninstall python-docx pypdf python-pptx

# 重新安装
pip install python-docx pypdf python-pptx openpyxl chardet pandas
```

---

## 🔍 故障排查

### 问题 1: 安装后仍然报错

**可能原因**: 服务未重启

**解决**:
1. 停止当前服务（Ctrl+C）
2. 确认进程已结束
3. 重新启动服务

### 问题 2: 多个 Python 版本

**检查**:
```bash
# 查看 Python 路径
where python

# 查看 pip 路径
where pip

# 确保它们指向同一个 Python 安装
```

**解决**: 使用完整路径
```bash
C:\Python312\python.exe -m pip install python-docx
```

### 问题 3: 权限问题

**症状**: 安装时提示权限不足

**解决**: 使用管理员权限运行终端，或添加 `--user` 参数
```bash
pip install --user python-docx
```

---

## 📦 完整的依赖列表

查看 `requirements.txt` 获取完整的依赖列表：

```txt
# Web框架
fastapi==0.104.1
uvicorn==0.24.0

# 数据验证
pydantic==2.5.0
pydantic-settings==2.1.0

# 数据库
sqlalchemy==2.0.23
psycopg2-binary==2.9.9

# 向量数据库
chromadb==0.4.18

# Embedding
sentence-transformers==2.2.2
numpy==1.26.2

# 文档处理
pypdf==3.17.1          # PDF
python-docx==1.1.0     # Word
python-pptx==0.6.23    # PowerPoint
openpyxl==3.1.2        # Excel
chardet==5.2.0         # 编码检测
pandas                 # 数据处理

# 其他
python-multipart==0.0.6
httpx==0.25.2
redis==5.0.1
```

---

## ✨ 总结

✅ **已完成**:
- 安装了所有文档处理依赖
- 创建了依赖检查脚本
- 验证所有库正确安装

🎯 **下一步**:
1. **重启服务**（必须！）
2. 测试上传 Word 文档
3. 测试其他格式（PDF、PPT、Excel）

**重启服务后，Word 文档上传应该能正常工作了！** 🎉

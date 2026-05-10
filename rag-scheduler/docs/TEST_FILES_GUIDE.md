# 测试文档准备指南

## 📝 如何创建测试文档

为了充分测试文档上传和解析功能，建议准备以下类型的测试文件：

---

## 1. PDF 文档测试

### 测试要点
- ✅ 普通文本PDF
- ✅ 包含表格的PDF
- ✅ 多栏布局PDF
- ⚠️ 扫描版PDF（需要OCR，当前不支持）

### 创建方法
**方法一**: 使用 Word 导出
1. 在 Word 中编写内容
2. 文件 → 另存为 → 选择 PDF 格式

**方法二**: 在线生成
- 访问 https://www.ilovepdf.com/zh-cn/word_to_pdf
- 上传 Word 文档转换为 PDF

### 推荐测试内容
```
标题: KRET-RAG 系统技术文档

第一章: 系统架构
1.1 微服务设计
1.2 数据流图

第二章: 功能模块
2.1 文档处理
2.2 向量检索
2.3 LLM集成

页脚: Page 1 of 5
水印: CONFIDENTIAL
```

---

## 2. Word 文档测试 (DOCX)

### 测试要点
- ✅ 段落文本
- ✅ 表格数据
- ✅ 列表项
- ✅ 标题层级

### 创建方法
直接使用 Microsoft Word 或 WPS 创建

### 推荐测试内容
创建一个包含以下元素的文档：
```
# 项目需求文档

## 背景介绍
这是一个RAG系统的开发文档...

## 功能列表
1. 文档上传
2. 文本解析
3. 向量存储

## 数据表格
| 模块 | 负责人 | 状态 |
|------|--------|------|
| 前端 | 张三   | 进行中 |
| 后端 | 李四   | 已完成 |

页眉: 内部资料
页脚: 第 1 页
```

---

## 3. PowerPoint 演示文稿测试 (PPTX)

### 测试要点
- ✅ 幻灯片标题
- ✅ 正文内容
- ✅ 多张幻灯片

### 创建方法
使用 Microsoft PowerPoint 或 WPS 演示

### 推荐测试内容
创建 3-5 张幻灯片：
```
Slide 1: 封面
- 标题: KRET-RAG 项目介绍
- 副标题: 智能文档问答系统

Slide 2: 核心功能
- 文档解析
- 向量检索
- 智能问答

Slide 3: 技术栈
- FastAPI
- ChromaDB
- OpenAI GPT
```

---

## 4. Excel 表格测试 (XLSX/CSV)

### 测试要点
- ✅ 单个工作表
- ✅ 多个工作表
- ✅ 包含中文
- ✅ CSV 格式

### 创建方法
**Excel**: 使用 Microsoft Excel 创建
**CSV**: 用记事本保存为 .csv 格式

### 推荐测试内容

**工作表1 - 员工信息**:
```
| 姓名 | 部门 | 职位 | 入职日期 |
|------|------|------|----------|
| 张三 | 技术部 | 工程师 | 2023-01-15 |
| 李四 | 产品部 | 经理 | 2022-06-20 |
```

**工作表2 - 销售数据**:
```
| 月份 | 销售额 | 订单数 |
|------|--------|--------|
| 1月 | 100000 | 150 |
| 2月 | 120000 | 180 |
```

---

## 5. 文本文件测试 (TXT/MD)

### 测试要点
- ✅ UTF-8 编码
- ✅ GBK 编码（中文Windows常见）
- ✅ Markdown 格式
- ✅ 长文本

### 创建方法
直接用记事本或 VS Code 创建

### 推荐测试内容

**test.txt** (UTF-8):
```
这是一段测试文本。

包含多个段落和空行。

用于测试文本文件的解析和清理功能。

特殊字符测试：@#$%^&*()
中英文混合：Hello 世界 World
```

**test.md** (Markdown):
```markdown
# 测试文档

## 第一章

这是**粗体**和*斜体*文本。

### 列表
- 项目1
- 项目2
- 项目3

## 第二章

> 引用文本

代码块：
```python
print("Hello World")
```
```

---

## 6. 边界情况测试

### 大文件测试
- 创建一个 5-8 MB 的 PDF 文档
- 验证是否能在 10MB 限制内正常上传

### 特殊字符测试
创建包含以下内容的文档：
```
特殊符号: © ® ™ € £ ¥
数学符号: ∑ ∫ ∂ ∇ √
箭头符号: ← → ↑ ↓ ↔
表情符号: 😀 😃 😄 😁
```

### 空文档测试
- 创建一个空白 PDF
- 验证错误处理

### 加密文档测试
- 创建一个带密码的 PDF
- 验证错误提示

---

## 📦 快速生成测试文件脚本

创建一个 Python 脚本来自动生成测试文件：

```python
# generate_test_files.py
from docx import Document
from pptx import Presentation
import pandas as pd

# 1. 生成 Word 文档
doc = Document()
doc.add_heading('测试文档', 0)
doc.add_paragraph('这是一个测试段落。')
table = doc.add_table(rows=2, cols=2)
table.cell(0, 0).text = '姓名'
table.cell(0, 1).text = '年龄'
table.cell(1, 0).text = '张三'
table.cell(1, 1).text = '25'
doc.save('test.docx')

# 2. 生成 Excel 文档
df1 = pd.DataFrame({'姓名': ['张三', '李四'], '年龄': [25, 30]})
df2 = pd.DataFrame({'月份': ['1月', '2月'], '销售额': [100, 200]})
with pd.ExcelWriter('test.xlsx') as writer:
    df1.to_excel(writer, sheet_name='员工信息', index=False)
    df2.to_excel(writer, sheet_name='销售数据', index=False)

# 3. 生成 PPT
prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "测试演示"
prs.save('test.pptx')

print("测试文件生成完成！")
```

运行：
```bash
pip install python-docx pandas openpyxl python-pptx
python generate_test_files.py
```

---

## ✅ 测试检查清单

上传每个文件后，验证以下内容：

- [ ] 文件成功上传（状态显示"✓ 成功"）
- [ ] 返回了 document_id
- [ ] 显示了提取的字符数
- [ ] 文件保存在 `uploads/` 目录
- [ ] 文本内容正确提取（无乱码）
- [ ] 页眉页脚已被去除
- [ ] 多余空白已清理
- [ ] 表格内容格式正确

---

## 🎯 推荐的测试顺序

1. **基础测试**: TXT 文件（最简单）
2. **常用格式**: PDF、DOCX
3. **办公文档**: PPTX、XLSX
4. **边界情况**: 大文件、特殊字符
5. **批量测试**: 同时上传多个文件

---

准备好测试文件后，就可以打开 `upload_test.html` 开始测试了！

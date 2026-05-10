# 表格转换问题调试指南

## 🔍 如何诊断表格转换问题

### 步骤 1: 运行测试脚本

```bash
cd rag-scheduler
python test_table_markdown.py
```

这个脚本会：
- ✅ 显示文档/工作表的基本信息（行数、列数）
- ✅ 展示转换后的 Markdown 输出
- ✅ 帮助你看到实际的转换结果

### 步骤 2: 准备测试文件

将包含表格的文件重命名并放到项目根目录：

**对于 DOCX**:
```bash
# 将你的文件复制并重命名
cp uploads/your_file.docx test_table.docx
```

**对于 Excel**:
```bash
cp uploads/your_file.xlsx test_table.xlsx
```

### 步骤 3: 查看输出

运行测试脚本后，你会看到类似这样的输出：

```
============================================================
测试 DOCX 表格转换
============================================================

📄 文档信息:
   段落数: 5
   表格数: 2

📊 表格 1:
   行数: 4
   第一行列数: 3

   Markdown 输出:
   --------------------------------------------------------
   | 姓名   | 年龄 | 城市 |
   |--------|------|------|
   | 张三   | 25   | 北京 |
   | 李四   | 30   | 上海 |
   --------------------------------------------------------
```

## 🐛 常见问题及解决方案

### 问题 1: 表格列数不一致

**症状**: 
- 某些行的单元格数量不同
- Markdown 表格对齐混乱

**原因**: 
- python-docx 对合并单元格的处理方式
- 原始表格存在合并单元格

**解决方案**:
代码已自动处理：
```python
# 确保所有行的列数一致
normalized_row = row[:max_cols]  # 截取到最大列数
while len(normalized_row) < max_cols:
    normalized_row.append("")
```

### 问题 2: 空行或空白单元格

**症状**:
- 输出中包含很多空行
- 表格中有大量空白单元格

**解决方案**:
代码已自动过滤：
```python
# 过滤掉全空的行
filtered_rows = [
    row for row in normalized_rows 
    if any(cell.strip() for cell in row)
]
```

### 问题 3: Markdown 格式不正确

**期望格式**:
```markdown
| 列1   | 列2   | 列3   |
|-------|-------|-------|
| 值1   | 值2   | 值3   |
```

**检查点**:
1. 表头是否有 `|` 分隔符
2. 分隔线是否使用 `-` 字符
3. 每行的列数是否一致

### 问题 4: 特殊字符处理

**症状**:
- 单元格中的 `|` 符号破坏表格结构
- 换行符导致格式混乱

**解决方案**:
代码已自动清理：
```python
cell_text = cell.text.strip().replace('\n', ' ').replace('\r', '')
```

## 📝 手动检查表格数据

如果测试脚本输出的结果仍不正确，可以手动检查原始数据：

### 对于 DOCX

```python
from docx import Document

doc = Document("test_table.docx")
table = doc.tables[0]  # 第一个表格

print(f"行数: {len(table.rows)}")
for i, row in enumerate(table.rows):
    print(f"行 {i}: {len(row.cells)} 个单元格")
    for j, cell in enumerate(row.cells):
        print(f"  单元格 [{i},{j}]: '{cell.text}'")
```

### 对于 Excel

```python
from openpyxl import load_workbook

wb = load_workbook("test_table.xlsx", data_only=True)
ws = wb.active

print(f"最大行: {ws.max_row}, 最大列: {ws.max_column}")
for row in ws.iter_rows(values_only=True):
    print(f"行数据: {row}")
```

## 🔧 调整转换逻辑

如果默认转换不符合你的需求，可以修改以下参数：

### 1. 调整列宽计算

当前使用左对齐：
```python
cell.ljust(col_widths[i])  # 左对齐
```

可以改为：
```python
cell.center(col_widths[i])  # 居中对齐
cell.rjust(col_widths[i])   # 右对齐
```

### 2. 调整表头检测

当前假设第一行是表头。如果需要智能检测：

```python
# 简单启发式：如果第一行都是短文本，可能是表头
def is_header(row):
    return all(len(cell) < 50 for cell in row)
```

### 3. 调整空行过滤

当前过滤全空行。如果需要保留部分空行：

```python
# 只过滤连续的空行
filtered_rows = []
consecutive_empty = 0
for row in normalized_rows:
    if any(cell.strip() for cell in row):
        filtered_rows.append(row)
        consecutive_empty = 0
    elif consecutive_empty < 1:  # 允许一个空行
        filtered_rows.append(row)
        consecutive_empty += 1
```

## 📊 示例对比

### 原始 DOCX 表格
```
+----------+--------+--------+
| 姓名     | 年龄   | 城市   |
+----------+--------+--------+
| 张三     | 25     | 北京   |
| 李四     | 30     | 上海   |
+----------+--------+--------+
```

### 转换后的 Markdown
```markdown
| 姓名   | 年龄 | 城市 |
|--------|------|------|
| 张三   | 25   | 北京 |
| 李四   | 30   | 上海 |
```

### 在 Markdown 阅读器中渲染
| 姓名   | 年龄 | 城市 |
|--------|------|------|
| 张三   | 25   | 北京 |
| 李四   | 30   | 上海 |

## 💡 调试技巧

### 1. 启用详细日志

在 `.env` 文件中设置：
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

查看详细的转换日志：
```
DEBUG:app.services.document_service:表格转换完成: 4 行, 3 列
DEBUG:app.services.document_service:Excel工作表转换完成: Sheet1, 10 行, 5 列
```

### 2. 检查清洗后的文本文件

上传文件后，查看生成的文本文件：
```bash
cat uploads_text/{uuid}.txt
```

检查表格部分是否正确转换。

### 3. 使用在线 Markdown 预览

将转换后的 Markdown 复制到：
- [Dillinger](https://dillinger.io/)
- [StackEdit](https://stackedit.io/)

查看渲染效果是否符合预期。

## 🎯 下一步

1. **运行测试脚本**，查看当前转换结果
2. **告诉我具体的问题**：
   - 哪些地方不对？
   - 期望的输出是什么？
   - 实际的输出是什么？
3. **提供示例文件**（如果可以），我可以帮你进一步调试

## 📚 相关文档

- [TABLE_TO_MARKDOWN.md](TABLE_TO_MARKDOWN.md) - 表格转 Markdown 功能说明
- [FILE_PROCESSING_FLOW.md](FILE_PROCESSING_FLOW.md) - 文件处理流程

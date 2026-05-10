# 表格转 Markdown 功能说明

## 📋 功能概述

rag-scheduler 服务现已支持将文档中的表格自动转换为 **Markdown 格式**，提升文本的可读性和结构化程度。

## 🎯 支持的格式

### 1. DOCX 文件（Word）
- ✅ 自动检测文档中的所有表格
- ✅ 转换为标准 Markdown 表格格式
- ✅ 保持列对齐和格式

### 2. Excel 文件（XLSX/XLS/CSV）
- ✅ 使用 Pandas 处理时转换为 Markdown
- ✅ 使用 openpyxl 处理时转换为 Markdown
- ✅ 多工作表支持，每个工作表单独转换

## 📝 Markdown 表格示例

### 输入（DOCX 表格）
```
姓名    | 年龄 | 城市
--------|------|------
张三    | 25   | 北京
李四    | 30   | 上海
王五    | 28   | 广州
```

### 输出（Markdown 格式）
```markdown
| 姓名   | 年龄 | 城市 |
|--------|------|------|
| 张三   | 25   | 北京 |
| 李四   | 30   | 上海 |
| 王五   | 28   | 广州 |
```

## 💻 实现细节

### 1. DOCX 表格转换

**方法**: `_convert_table_to_markdown(table)`

**处理流程**：
1. 遍历表格的所有行和单元格
2. 清理单元格内容（去除空白、替换换行符）
3. 计算每列的最大宽度（用于对齐）
4. 构建 Markdown 表头、分隔线、数据行
5. 返回格式化后的字符串

**代码位置**: [`app/services/document_service.py`](file://g:\rag\kret-rag\rag-scheduler\app\services\document_service.py#L328-L407)

**示例输出**：
```python
# 调用
markdown_table = self._convert_table_to_markdown(docx_table)

# 输出
"""
| 产品   | 价格  | 库存 |
|--------|-------|------|
| 苹果   | 5.00  | 100  |
| 香蕉   | 3.50  | 200  |
"""
```

### 2. Excel DataFrame 转换

**方法**: `_convert_dataframe_to_markdown(df)`

**处理流程**：
1. 获取 DataFrame 的列名作为表头
2. 将所有数据转换为字符串（处理 NaN 值）
3. 计算每列的最大宽度
4. 构建 Markdown 表格
5. 返回格式化后的字符串

**代码位置**: [`app/services/document_service.py`](file://g:\rag\kret-rag\rag-scheduler\app\services\document_service.py#L409-L467)

### 3. Excel 工作表转换

**方法**: `_convert_excel_sheet_to_markdown(worksheet, sheet_name)`

**处理流程**：
1. 遍历工作表的所有行
2. 跳过全空的行
3. 添加工作表标题（`### Sheet: xxx`）
4. 将第一行作为表头
5. 构建 Markdown 表格
6. 返回格式化后的字符串

**代码位置**: [`app/services/document_service.py`](file://g:\rag\kret-rag\rag-scheduler\app\services\document_service.py#L469-L543)

## 🔄 处理流程

### DOCX 文件
```
上传 DOCX 文件
    ↓
解析文档结构
    ↓
提取段落文本
    ↓
⭐ 检测表格
    ↓
⭐ 转换为 Markdown 格式
    ↓
添加到文本内容
    ↓
继续后续处理（清理、保存等）
```

### Excel 文件
```
上传 Excel 文件
    ↓
读取数据到 DataFrame/Worksheet
    ↓
⭐ 转换为 Markdown 表格
    ↓
添加工作表标题
    ↓
合并所有工作表内容
    ↓
继续后续处理
```

## 📊 日志记录

### DOCX 表格
```
INFO:app.services.document_service:提取了 50 个段落
INFO:app.services.document_service:提取了 3 个表格
INFO:app.services.document_service:DOCX 文本提取完成，总长度: 15000 字符
```

### Excel 表格
```
INFO:app.services.document_service:开始提取 Excel 数据
INFO:app.services.document_service:Excel 数据转换完成
```

## 🧪 测试示例

### 测试 DOCX 表格

创建包含表格的 DOCX 文件：
```
+----------+--------+--------+
| 姓名     | 年龄   | 城市   |
+----------+--------+--------+
| 张三     | 25     | 北京   |
| 李四     | 30     | 上海   |
+----------+--------+--------+
```

上传后查看 `uploads_text/{uuid}.txt`：
```markdown
这是文档的开头部分...

| 姓名   | 年龄 | 城市 |
|--------|------|------|
| 张三   | 25   | 北京 |
| 李四   | 30   | 上海 |

这是文档的结尾部分...
```

### 测试 Excel 文件

创建 Excel 文件，包含两个工作表：

**Sheet1: 员工信息**
```
+----------+--------+--------+
| 姓名     | 部门   | 职位   |
+----------+--------+--------+
| 张三     | 技术部 | 工程师 |
| 李四     | 市场部 | 经理   |
+----------+--------+--------+
```

**Sheet2: 产品信息**
```
+----------+--------+--------+
| 产品     | 价格   | 库存   |
+----------+--------+--------+
| 苹果     | 5.00   | 100    |
| 香蕉     | 3.50   | 200    |
+----------+--------+--------+
```

上传后查看 `uploads_text/{uuid}.txt`：
```markdown
### Sheet: 员工信息

| 姓名   | 部门   | 职位   |
|--------|--------|--------|
| 张三   | 技术部 | 工程师 |
| 李四   | 市场部 | 经理   |

### Sheet: 产品信息

| 产品   | 价格 | 库存 |
|--------|------|------|
| 苹果   | 5.00 | 100  |
| 香蕉   | 3.50 | 200  |
```

## 💡 优势

### 1. 更好的可读性
- ✅ Markdown 表格在文本编辑器中清晰易读
- ✅ 支持 GitHub、GitLab 等平台渲染
- ✅ 便于人工检查和编辑

### 2. 结构化数据
- ✅ 保持表格的行列结构
- ✅ 便于后续的向量化和检索
- ✅ LLM 更容易理解表格内容

### 3. 兼容性
- ✅ 标准的 Markdown 语法
- ✅ 大多数 Markdown 解析器支持
- ✅ 可轻松转换为 HTML、PDF 等格式

### 4. 容错性
- ✅ 转换失败时降级为简单文本格式
- ✅ 详细的错误日志
- ✅ 不影响整体文档处理流程

## 🔍 注意事项

### 1. 复杂表格
- ⚠️ 合并单元格可能被展平
- ⚠️ 嵌套表格可能无法正确转换
- ⚠️ 建议简化表格结构

### 2. 大表格
- ⚠️ 非常大的表格可能影响性能
- ⚠️ 建议拆分为多个小表格
- ⚠️ 考虑分页显示

### 3. 特殊字符
- ⚠️ 单元格中的 `|` 符号会被转义
- ⚠️ 换行符被替换为空格
- ⚠️ 建议在上传前清理特殊字符

## 🚀 未来改进方向

1. **智能表头检测**
   - 自动识别表头行
   - 支持多行表头
   - 根据内容判断表头位置

2. **表格样式保留**
   - 保留单元格对齐方式
   - 保留字体样式（粗体、斜体）
   - 保留背景色信息

3. **嵌套表格支持**
   - 递归处理嵌套表格
   - 生成层级化的 Markdown

4. **表格元数据**
   - 记录表格位置
   - 记录表格标题
   - 记录表格编号

5. **性能优化**
   - 异步处理大表格
   - 流式处理超大文件
   - 缓存常用转换结果

## 📚 相关文档

- [FILE_PROCESSING_FLOW.md](FILE_PROCESSING_FLOW.md) - 文件处理流程
- [CLEANED_TEXT_AUTO_SAVE.md](CLEANED_TEXT_AUTO_SAVE.md) - 清洗后文本保存
- [DOCX_EXTRACTION_ERROR_GUIDE.md](DOCX_EXTRACTION_ERROR_GUIDE.md) - DOCX 错误处理

## 🔗 参考资料

- [Markdown 表格语法](https://www.markdownguide.org/basic-syntax/#tables)
- [python-docx 文档](https://python-docx.readthedocs.io/)
- [Pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html)
- [openpyxl 文档](https://openpyxl.readthedocs.io/)

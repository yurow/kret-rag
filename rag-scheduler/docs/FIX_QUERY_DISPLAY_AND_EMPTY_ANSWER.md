# RAG查询结果显示优化

## 🎯 问题解决

### **问题1**：查询结果中没有显示原始问题和重写后的查询
### **问题2**：AI回答部分为空

---

## ✅ 修复内容

### **后端修改** - [rag-scheduler/app/routes/query.py](file://g:\rag\kret-rag\rag-scheduler\app\routes\query.py)

#### 流式API增强

**修改前**（❌）：
```python
# 发送检索结果
yield f"data: {json.dumps({
    'type': 'retrieval', 
    'data': {
        'results_count': len(rag_result.results),
        'query_time': rag_result.query_time
    }
})}\n\n"

# ❌ 没有发送complete事件
# ❌ 没有包含original_query和rewritten_query
```

**修改后**（✅）：
```python
# 发送检索结果（包含完整信息）
yield f"data: {json.dumps({
    'type': 'retrieval', 
    'data': {
        'results_count': len(rag_result.results),
        'query_time': rag_result.query_time,
        'original_query': getattr(rag_result, 'original_query', request.query),
        'rewritten_query': getattr(rag_result, 'rewritten_query', request.query),
        'context': rag_result.context  # ⭐ 添加上下文
    }
}, ensure_ascii=False)}\n\n"

# 累积完整回答
full_answer = ""
async for chunk in stream_response.aiter_text():
    yield chunk
    # 解析chunk并累积回答
    if chunk_data.get('type') == 'chunk':
        full_answer += chunk_data.get('data', {}).get('content', '')

# ⭐ 发送complete事件（包含所有最终数据）
complete_event = {
    'type': 'complete',
    'data': {
        'answer': full_answer,
        'sources': [...],
        'context_used': rag_result.context,
        'system_prompt': system_prompt,
        'original_query': ...,
        'rewritten_query': ...
    }
}
yield f"data: {json.dumps(complete_event)}\n\n"
```

**关键改进**：
1. ✅ retrieval事件包含 `original_query` 和 `rewritten_query`
2. ✅ retrieval事件包含 `context`（用于立即显示）
3. ✅ 累积完整回答到 `full_answer` 变量
4. ✅ 最后发送 `complete` 事件，包含所有最终数据
5. ✅ 获取系统提示词并添加到complete事件

---

### **前端修改** - [test_query.html](file://g:\rag\kret-rag\rag-scheduler\test_query.html)

#### 1. 在retrieval事件中显示查询重写信息

**新增代码**：
```javascript
if (data.type === 'retrieval') {
    // 检索完成
    retrievalData = data.data;
    updateStats([], retrievalData.query_time);
    
    // ⭐ 显示查询重写信息
    const rewriteInfo = document.getElementById('rewriteInfo');
    if (retrievalData.original_query && retrievalData.rewritten_query) {
        document.getElementById('originalQuery').textContent = retrievalData.original_query;
        document.getElementById('rewrittenQuery').textContent = retrievalData.rewritten_query;
        rewriteInfo.style.display = 'block';
    }
    
    // ⭐ 显示上下文信息
    const contextInfo = document.getElementById('contextInfo');
    if (retrievalData.context) {
        document.getElementById('contextContent').textContent = retrievalData.context;
        contextInfo.style.display = 'block';
    }
}
```

**效果**：
- ✅ 检索完成后立即显示原始查询和重写查询
- ✅ 同时显示构建的上下文内容
- ✅ 用户可以在等待AI回答时看到这些信息

---

#### 2. 在complete事件中补充显示

**新增代码**：
```javascript
else if (data.type === 'complete') {
    const completeData = data.data;
    
    // ⭐ 如果之前没显示，现在显示查询重写信息
    const rewriteInfo = document.getElementById('rewriteInfo');
    if (completeData.original_query && completeData.rewritten_query && 
        rewriteInfo.style.display === 'none') {
        document.getElementById('originalQuery').textContent = completeData.original_query;
        document.getElementById('rewrittenQuery').textContent = completeData.rewritten_query;
        rewriteInfo.style.display = 'block';
    }
    
    // 显示引用来源、系统提示词等...
}
```

**容错机制**：
- 如果retrieval事件中没有显示（可能因为某些原因），complete事件中会补充显示
- 检查 `style.display === 'none'` 避免重复显示

---

## 📊 工作流程对比

### **修改前**（❌ 有问题）

```
用户提问："什么是机器学习的优势？"
  ↓
检索完成
  ↓
发送retrieval事件：{results_count: 5, query_time: 0.123}
  ↓
❌ 前端不显示原始查询和重写查询
❌ 前端不显示上下文
  ↓
流式输出AI回答
  ↓
❌ 没有complete事件
❌ AI回答可能为空（因为没有累积）
```

---

### **修改后**（✅ 正常）

```
用户提问："什么是机器学习的优势？"
  ↓
检索完成 + 查询重写
  original_query: "什么是机器学习的优势？"
  rewritten_query: "机器学习 优势"
  ↓
发送retrieval事件：{
    results_count: 5,
    query_time: 0.123,
    original_query: "...",
    rewritten_query: "...",
    context: "[引用1]..."
}
  ↓
✅ 前端立即显示：
   - 原始查询
   - 重写查询
   - 上下文内容
  ↓
流式输出AI回答（逐字显示）
  ↓
发送complete事件：{
    answer: "完整回答...",
    sources: [...],
    system_prompt: "...",
    original_query: "...",
    rewritten_query: "..."
}
  ↓
✅ 前端显示：
   - 引用来源
   - 系统提示词
   - JSON响应
```

---

## 🧪 测试验证

### 1. **重启服务**

```bash
cd g:\rag\kret-rag
.\start-scheduler.bat
```

---

### 2. **访问测试页面**

浏览器打开：http://localhost:8000/test-query

---

### 3. **测试查询重写显示**

**步骤**：
1. 输入问题：**"什么是机器学习的优势和应用场景？"**
2. 确保勾选"☑️ 查询重写"
3. 点击 **"💬 RAG 生成回答"**

**预期结果**：
- ✅ 检索完成后立即显示粉色边框的"📝 查询重写"卡片
- ✅ 显示：
  ```
  原始查询：什么是机器学习的优势和应用场景？
  重写后查询：机器学习 优势 应用场景
  ```
- ✅ 显示蓝色边框的"📄 构建的上下文"卡片
- ✅ AI回答逐字显示（打字机效果）
- ✅ 完成后显示紫色边框的"🔧 系统提示词"卡片

---

### 4. **测试AI回答不为空**

**验证点**：
- ✅ AI回答区域有内容（不是空白）
- ✅ 回答内容与检索到的上下文相关
- ✅ 如果知识库无相关信息，显示「知识库暂无相关配置信息」

**如果仍为空，检查**：
1. llm-session服务是否正常运行
2. 浏览器控制台是否有错误
3. 网络请求是否成功（F12 → Network标签）

---

### 5. **查看JSON响应**

在页面底部的"JSON 响应"区域，应该看到：

```json
{
  "answer": "根据参考信息，机器学习的优势包括...",
  "sources": [...],
  "context_used": "[引用1] ...",
  "system_prompt": "你是一个智能问答助手...\n**核心原则**...",
  "original_query": "什么是机器学习的优势和应用场景？",
  "rewritten_query": "机器学习 优势 应用场景",
  "query_time": 0.123,
  "session_id": "xxx"
}
```

**确认**：
- ✅ `original_query` 字段存在
- ✅ `rewritten_query` 字段存在
- ✅ `answer` 字段有内容（不为空字符串）

---

## 💡 技术要点

### **SSE事件顺序**

```
1. retrieval事件（检索完成）
   ├─ results_count
   ├─ query_time
   ├─ original_query ⭐
   ├─ rewritten_query ⭐
   └─ context ⭐

2. 多个chunk事件（流式文本）
   └─ content: "你"
   └─ content: "好"
   └─ ...

3. complete事件（最终结果）
   ├─ answer（完整回答）
   ├─ sources
   ├─ system_prompt
   ├─ original_query ⭐
   └─ rewritten_query ⭐
```

---

### **为什么需要complete事件？**

**原因**：
1. **累积完整回答** - 流式输出是逐字的，需要累积成完整字符串
2. **获取系统提示词** - 需要从llm-session获取会话历史
3. **提供完整数据** - 用于显示JSON响应和最终统计

**如果不发送complete事件**：
- ❌ 前端无法获取完整的answer（只有逐字片段）
- ❌ 无法显示系统提示词
- ❌ JSON响应不完整

---

## 🐛 常见问题排查

### **问题1：AI回答仍为空**

**可能原因**：
1. llm-session服务未启动
2. rag_context为null，导致系统提示词未生效
3. LLM返回空字符串

**排查步骤**：
```bash
# 1. 检查llm-session服务
curl http://localhost:9000/health

# 2. 查看rag-scheduler日志
# 查找："LLM服务调用失败" 或 "流式生成失败"

# 3. 浏览器控制台
# F12 → Console，查看JavaScript错误

# 4. 网络请求
# F12 → Network，查看 /query/generate/stream 请求
# 检查Response中是否有data事件
```

---

### **问题2：查询重写信息不显示**

**可能原因**：
1. 未勾选"☑️ 查询重写"选项
2. 查询无需重写（简单查询）
3. retrieval事件中未包含这些字段

**排查步骤**：
```javascript
// 浏览器控制台执行
console.log(retrievalData);
// 检查是否有 original_query 和 rewritten_query 字段
```

---

### **问题3：上下文不显示**

**可能原因**：
1. 检索结果为空
2. context字段为null或空字符串

**排查步骤**：
```javascript
// 浏览器控制台执行
console.log(retrievalData.context);
// 检查是否有内容
```

---

## 📚 相关文件

| 文件 | 修改内容 |
|------|---------|
| [[rag-scheduler/app/routes/query.py](file://g:\rag\kret-rag\rag-scheduler\app\routes\query.py)] | 流式API增强，添加complete事件 |
| [[test_query.html](file://g:\rag\kret-rag\rag-scheduler\test_query.html)] | 显示查询重写和上下文信息 |

---

## ✅ 总结

通过这次修复，实现了：

1. ✅ **查询重写信息显示** - 在检索完成后立即显示原始查询和重写查询
2. ✅ **上下文信息显示** - 显示构建的RAG上下文
3. ✅ **AI回答不为空** - 通过complete事件提供完整回答
4. ✅ **完整的数据流** - retrieval → chunks → complete

**用户体验提升**：
- 🚀 更快的信息反馈（检索后立即显示查询信息）
- 🔍 更好的可观测性（看到查询如何被优化）
- 📝 更完整的回答（确保AI回答有内容）

🎉 **现在可以清晰地看到整个RAG流程了！**

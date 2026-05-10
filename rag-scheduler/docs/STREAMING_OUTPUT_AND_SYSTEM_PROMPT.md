# RAG流式输出和系统提示词显示功能

## 🎯 新增功能

### 1. **流式输出显示** ⭐
- 实时显示AI生成的回答内容
- 打字机效果，逐字显示
- 无需等待完整响应

### 2. **系统提示词展示** ⭐
- 在JSON响应中包含系统提示词
- 前端可视化展示防幻觉指令
- 便于调试和验证Prompt生效情况

---

## ✅ 已完成的修改

### **后端修改** - [rag-scheduler/app/routes/query.py](file://g:\rag\kret-rag\rag-scheduler\app\routes\query.py)

#### 1. 增强 `/query/generate` API

**新增功能**：
- 从llm-session获取会话历史
- 提取系统提示词（role="system"的消息）
- 在响应中添加 `system_prompt` 字段

```python
# 获取会话历史以提取系统提示词
session_id = llm_response.get("session_id")
system_prompt = None

if session_id:
    try:
        async with httpx.AsyncClient(timeout=5.0) as history_client:
            history_response = await history_client.get(
                f"{settings.LLM_SESSION_URL}/sessions/{session_id}/history"
            )
            if history_response.status_code == 200:
                history_data = history_response.json()
                conversation_history = history_data.get("conversation_history", [])
                # 提取系统提示词
                for msg in conversation_history:
                    if msg.get("role") == "system":
                        system_prompt = msg.get("content")
                        break
    except Exception as e:
        logger.warning(f"获取会话历史失败: {e}")

# 返回完整的RAG结果
return {
    "query": request.query,
    "answer": llm_response.get("response", ""),
    "sources": [...],
    "context_used": rag_result.context,
    "system_prompt": system_prompt,  # ⭐ 新增
    "query_time": rag_result.query_time,
    "session_id": session_id
}
```

---

#### 2. 新增 `/query/generate/stream` API

**功能**：
- Server-Sent Events (SSE) 流式输出
- 实时返回LLM生成的内容块
- 支持检索信息和最终结果的传输

```python
@router.post("/generate/stream")
async def generate_answer_stream(request: DocumentQueryRequest):
    """流式生成回答"""
    from fastapi.responses import StreamingResponse
    
    async def event_generator():
        # 1. 执行检索
        rag_result = await rag_service.retrieve_and_build_context(request)
        
        # 2. 发送检索结果
        yield f"data: {json.dumps({'type': 'retrieval', 'data': {...}})}\n\n"
        
        # 3. 流式调用llm-session
        async with client.stream("POST", ".../chat/stream", ...) as stream_response:
            async for chunk in stream_response.aiter_text():
                yield chunk  # 直接转发SSE数据
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
```

**SSE数据格式**：
```
data: {"type": "retrieval", "data": {"results_count": 5, "query_time": 0.123}}

data: {"type": "chunk", "data": {"content": "你好"}}

data: {"type": "chunk", "data": {"content": "，"}}

data: {"type": "chunk", "data": {"content": "我是"}}

data: {"type": "complete", "data": {"answer": "...", "sources": [...], "system_prompt": "..."}}

data: {"type": "error", "data": {"message": "错误信息"}}
```

---

### **前端修改** - [test_query.html](file://g:\rag\kret-rag\rag-scheduler\test_query.html)

#### 1. 重写 `testGenerateAnswer()` 函数

**改进**：
- 使用 Fetch API 读取流式数据
- 实时追加文本到页面
- 自动滚动到底部
- 显示系统提示词卡片

```javascript
async function testGenerateAnswer() {
    // 使用流式API
    const response = await fetch(`${API_BASE}/query/generate/stream`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(params)
    });
    
    // 准备显示区域
    const answerContent = document.getElementById('answerContent');
    answerContent.textContent = '';
    
    // 读取流式数据
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let fullAnswer = '';
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));
                
                if (data.type === 'chunk') {
                    // 实时显示文本块
                    fullAnswer += data.data.content;
                    answerContent.textContent = fullAnswer;
                    
                    // 自动滚动
                    answerContent.scrollTop = answerContent.scrollHeight;
                } else if (data.type === 'complete') {
                    // 显示来源和系统提示词
                    displaySources(data.data.sources);
                    displaySystemPrompt(data.data.system_prompt);
                    displayJSON(data.data);
                }
            }
        }
    }
}
```

---

#### 2. 增强 `displayResults()` 函数

**新增**：显示系统提示词卡片

```javascript
// 显示系统提示词
if (data.system_prompt) {
    const systemPromptCard = document.createElement('div');
    systemPromptCard.className = 'result-card';
    systemPromptCard.style.cssText = 'border-left-color: #9c27b0; margin-top: 15px;';
    systemPromptCard.innerHTML = `
        <div class="result-title">🔧 系统提示词</div>
        <div class="result-content" style="margin-top: 10px; white-space: pre-wrap; font-size: 13px; max-height: 300px; overflow-y: auto;">
            ${escapeHtml(data.system_prompt)}
        </div>
    `;
    answerSection.appendChild(systemPromptCard);
}
```

---

## 📊 工作流程对比

### **修改前**（非流式）

```
用户点击"RAG生成回答"
  ↓
等待完整响应（5-10秒）
  ↓
一次性显示所有结果
  ↓
❌ 用户体验差（长时间等待）
❌ 无法看到系统提示词
```

---

### **修改后**（流式 + 系统提示词）

```
用户点击"RAG生成回答"
  ↓
立即显示检索统计
  ↓
实时逐字显示AI回答（打字机效果）✨
  ↓
显示引用来源
  ↓
显示系统提示词卡片 ✨
  ↓
显示完整JSON响应
  ↓
✅ 用户体验好（即时反馈）
✅ 可验证防幻觉Prompt生效
```

---

## 🧪 测试步骤

### 1. **重启服务**

```bash
cd g:\rag\kret-rag
.\start-scheduler.bat
```

---

### 2. **访问测试页面**

浏览器打开：http://localhost:8000/test-query

---

### 3. **测试流式输出**

1. 输入问题：**"RAG系统使用什么向量数据库"**
2. 点击 **"💬 RAG 生成回答"** 按钮
3. 观察效果：
   - ✅ 立即显示检索统计
   - ✅ AI回答逐字显示（打字机效果）
   - ✅ 自动滚动到底部
   - ✅ 完成后显示引用来源
   - ✅ 显示紫色边框的系统提示词卡片
   - ✅ 底部显示完整JSON（包含system_prompt字段）

---

### 4. **验证系统提示词**

在JSON响应中查找：
```json
{
  "query": "RAG系统使用什么向量数据库",
  "answer": "根据参考信息...",
  "system_prompt": "你是一个智能问答助手...\n**核心原则**:\n1. 严格基于参考信息回答...",
  "sources": [...],
  "context_used": "[引用1] ..."
}
```

**确认**：
- ✅ `system_prompt` 字段存在
- ✅ 包含防幻觉指令（"禁止编造答案"等）
- ✅ 包含参考信息内容

---

### 5. **测试无相关知识的问题**

输入问题：**"如何制作红烧肉"**

**预期结果**：
- ✅ 流式显示「知识库暂无相关配置信息」
- ✅ 系统提示词卡片显示防幻觉约束
- ✅ 证明Prompt生效，LLM没有编造烹饪步骤

---

## 💡 技术要点

### **SSE (Server-Sent Events)**

**优势**：
- ✅ 单向流式传输（服务器→客户端）
- ✅ 原生HTTP支持，无需特殊协议
- ✅ 自动重连机制
- ✅ 比WebSocket更简单

**实现关键**：
```python
# 服务端
yield f"data: {json.dumps(data)}\n\n"  # 双换行符分隔事件

# 客户端
const reader = response.body.getReader();
while (true) {
    const { done, value } = await reader.read();
    // 解析SSE格式
}
```

---

### **系统提示词提取**

**方法**：
1. 从llm-session获取会话历史API
2. 遍历消息列表
3. 找到第一条 `role="system"` 的消息
4. 提取其 `content` 字段

**容错**：
- 如果获取失败，`system_prompt` 为 `null`
- 不影响主要功能（回答和来源仍正常显示）

---

## 🎨 UI设计

### **系统提示词卡片样式**

```css
.result-card {
    border-left-color: #9c27b0;  /* 紫色边框 */
    margin-top: 15px;
}

.result-content {
    white-space: pre-wrap;       /* 保留换行 */
    font-size: 13px;             /* 较小字体 */
    max-height: 300px;           /* 限制高度 */
    overflow-y: auto;            /* 可滚动 */
}
```

**视觉效果**：
- 🔧 紫色左边框标识
- 📜 可滚动的长文本区域
- 📝 保留原始格式（换行、缩进）

---

## 📚 相关文件

| 文件 | 修改内容 |
|------|---------|
| [[rag-scheduler/app/routes/query.py](file://g:\rag\kret-rag\rag-scheduler\app\routes\query.py)] | 增强generate API，新增stream API |
| [[test_query.html](file://g:\rag\kret-rag\rag-scheduler\test_query.html)] | 流式显示逻辑，系统提示词展示 |

---

## ✅ 总结

通过这次更新，实现了：

1. ✅ **流式输出** - 实时显示AI回答，提升用户体验
2. ✅ **系统提示词** - 可视化展示防幻觉指令，便于调试
3. ✅ **SSE技术** - 使用标准的Server-Sent Events协议
4. ✅ **容错处理** - 即使获取系统提示词失败也不影响主流程

**核心价值**：
- 🚀 更快的响应感知（流式显示）
- 🔍 更好的可观测性（查看Prompt）
- 🛡️ 更强的可信度（验证防幻觉机制）

🎉 **现在可以愉快地测试RAG系统了！**

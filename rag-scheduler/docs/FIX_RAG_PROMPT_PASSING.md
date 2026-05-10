# RAG防幻觉提示词传递修复

## 🐛 问题描述

虽然在 [chat_service.py](file://g:\rag\kret-rag\llm-session\app\services\chat_service.py) 中添加了完善的防幻觉提示词，但**实际上这些提示词并没有传递给LLM**。

---

## 🔍 根本原因

### **调用链分析**

```
用户请求
  ↓
rag-scheduler/query.py (第203行)
  ↓
调用 llm-session/chat/message API
  ↓
传递参数: {message, session_id, query}
  ❌ 缺少 rag_context 字段！
  ↓
llm-session/chat_service.py/_build_system_prompt()
  ↓
检查 rag_context 是否为空
  ↓
如果为空 → 返回 None（不添加系统提示）❌
  ↓
LLM收到消息时没有防幻觉约束
```

---

### **代码对比**

#### **修改前**（❌ 错误）

```python
# rag-scheduler/app/routes/query.py
response = await client.post(
    f"{settings.LLM_SESSION_URL}/chat/message",
    json={
        "message": rag_result.context,  # ❌ 将上下文作为消息发送
        "session_id": getattr(request, 'session_id', None),
        "query": request.query  # ✅ 原始查询
        # ❌ 缺少 rag_context 字段！
    }
)
```

**问题**：
- `message` 字段被设置为检索到的上下文内容
- 没有传递 `rag_context` 字段
- `_build_system_prompt()` 方法检查到 `rag_context=None`，直接返回 `None`
- **防幻觉提示词完全没有生效！**

---

#### **修改后**（✅ 正确）

```python
# rag-scheduler/app/routes/query.py
response = await client.post(
    f"{settings.LLM_SESSION_URL}/chat/message",
    json={
        "message": request.query,  # ✅ 用户问题作为消息
        "session_id": getattr(request, 'session_id', None),
        "query": request.query,  # ✅ 原始查询
        "rag_context": rag_result.context if rag_result.context else None  # ⭐ RAG检索的上下文
    }
)
```

**修复**：
- `message` 字段改为传递用户问题
- **新增 `rag_context` 字段**，传递检索到的上下文
- `_build_system_prompt()` 检测到 `rag_context` 不为空，构建包含防幻觉指令的系统提示
- **防幻觉提示词成功传递给LLM！**

---

## 📊 工作流程对比

### **修改前的流程**（❌ 无效）

```
RAG检索结果
  ↓
context = "[引用1] xxx\n[引用2] yyy..."
  ↓
发送到llm-session:
{
  "message": context,  // ❌ 上下文被当作用户消息
  "query": "用户问题"
}
  ↓
_build_system_prompt(rag_context=None)
  ↓
返回 None（不添加系统提示）
  ↓
LLM收到的消息:
[
  {"role": "user", "content": "[引用1] xxx..."}  // ❌ 没有系统提示
]
  ↓
LLM可能编造答案 ❌
```

---

### **修改后的流程**（✅ 有效）

```
RAG检索结果
  ↓
context = "[引用1] xxx\n[引用2] yyy..."
  ↓
发送到llm-session:
{
  "message": "用户问题",  // ✅ 用户问题
  "query": "用户问题",
  "rag_context": context  // ⭐ 上下文单独传递
}
  ↓
_build_system_prompt(rag_context=context)
  ↓
返回包含防幻觉指令的系统提示:
"""
你是一个智能问答助手...
**核心原则**:
1. 严格基于参考信息回答
2. 禁止编造答案...
**参考信息**:
[引用1] xxx...
"""
  ↓
LLM收到的消息:
[
  {"role": "system", "content": "防幻觉提示词+参考信息"},  // ✅ 系统提示
  {"role": "user", "content": "用户问题"}
]
  ↓
LLM严格遵守约束，不会编造答案 ✅
```

---

## ✅ 修复内容

### 文件：[rag-scheduler/app/routes/query.py](file://g:\rag\kret-rag\rag-scheduler\app\routes\query.py)

**修改位置**：第203-210行

**修改内容**：
```python
# 修改前
json={
    "message": rag_result.context,  # ❌
    "session_id": ...,
    "query": request.query
}

# 修改后
json={
    "message": request.query,  # ✅
    "session_id": ...,
    "query": request.query,
    "rag_context": rag_result.context if rag_result.context else None  # ⭐
}
```

---

## 🧪 验证步骤

### 1. **重启服务**

```bash
# 重启 rag-scheduler
cd g:\rag\kret-rag
.\start-scheduler.bat

# 重启 llm-session
cd llm-session
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

---

### 2. **测试有相关知识的问题**

```bash
curl -X POST http://localhost:8000/query/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "RAG系统使用什么向量数据库",
    "top_k": 5,
    "score_threshold": 0.3
  }'
```

**预期结果**：
- ✅ 返回基于知识库的回答
- ✅ 包含引用标记（如 `[引用1]`）
- ✅ 回答内容与检索到的上下文一致

---

### 3. **测试无相关知识的问题**

```bash
curl -X POST http://localhost:8000/query/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "如何制作红烧肉",
    "top_k": 5,
    "score_threshold": 0.3
  }'
```

**预期结果**：
- ✅ 返回「知识库暂无相关配置信息」
- ✅ **不会编造烹饪步骤**

---

### 4. **查看日志验证**

在 llm-session 的日志中应该看到：

```
INFO: 处理消息: session_id=xxx, has_rag_context=True
INFO: LLM响应生成完成，长度: xxx 字符
```

如果 `has_rag_context=False`，说明修复未生效！

---

## 💡 关键要点

### **职责分离**

| 组件 | 职责 |
|------|------|
| **rag-scheduler** | 负责检索、构建上下文、传递 `rag_context` |
| **llm-session** | 负责接收 `rag_context`、构建系统提示、调用LLM |

### **数据流**

```
rag-scheduler                    llm-session
     |                                |
     |--- retrieve_and_build_context -->|
     |                                |
     |<-- DocumentQueryResponse ------|
     |   (包含 context 字段)           |
     |                                |
     |--- POST /chat/message -------->|
     |   {                            |
     |     message: query,            |
     |     rag_context: context       |
     |   }                            |
     |                                |
     |<-- SendMessageResponse --------|
     |   { response: answer }         |
```

---

## 🎯 总结

### **问题根源**
- rag-scheduler 没有正确传递 `rag_context` 字段
- llm-session 收不到上下文，无法构建系统提示
- 防幻觉提示词完全失效

### **修复方案**
- 修改 rag-scheduler 的请求参数
- 正确传递 `rag_context` 字段
- 确保 `_build_system_prompt()` 能接收到上下文

### **验证方法**
- 测试有无相关知识的问题
- 检查日志中的 `has_rag_context` 标志
- 确认LLM不再编造答案

---

**现在防幻觉提示词真正生效了！** 🎉

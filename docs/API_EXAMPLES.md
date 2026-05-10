# KRET-RAG API 使用示例

本文档提供两个服务的API使用示例。

## 前置条件

1. 启动 rag-scheduler 服务（端口 8000）
2. 启动 llm-session 服务（端口 9000）

---

## rag-scheduler API 示例

### 1. 上传文档

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@/path/to/your/document.pdf" \
  -F 'metadata={"category": "technical", "author": "John Doe"}'
```

响应示例：
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Document uploaded successfully"
}
```

### 2. 查询文档（RAG检索+生成）

```bash
curl -X POST "http://localhost:8000/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是机器学习？",
    "top_k": 5,
    "score_threshold": 0.7
  }'
```

响应示例：
```json
{
  "results": [
    {
      "chunk_id": "chunk_001",
      "document_id": "550e8400-e29b-41d4-a716-446655440000",
      "content": "机器学习是人工智能的一个分支...",
      "score": 0.85,
      "metadata": {}
    }
  ],
  "total": 5,
  "query_time": 0.234
}
```

### 3. 仅执行向量搜索

```bash
curl -X POST "http://localhost:8000/query/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "深度学习",
    "top_k": 3,
    "score_threshold": 0.6
  }'
```

### 4. 获取文档信息

```bash
curl -X GET "http://localhost:8000/documents/550e8400-e29b-41d4-a716-446655440000"
```

### 5. 列出所有文档

```bash
curl -X GET "http://localhost:8000/documents/?page=1&page_size=10"
```

### 6. 删除文档

```bash
curl -X DELETE "http://localhost:8000/documents/550e8400-e29b-41d4-a716-446655440000"
```

---

## llm-session API 示例

### 1. 创建会话

```bash
curl -X POST "http://localhost:9000/sessions/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "session_name": "技术讨论",
    "metadata": {"topic": "AI"}
  }'
```

响应示例：
```json
{
  "session_id": "660e9500-f39c-52e5-b827-557766551111",
  "message": "Session created successfully"
}
```

### 2. 发送消息（完整响应）

```bash
curl -X POST "http://localhost:9000/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "请解释一下Transformer架构",
    "session_id": "660e9500-f39c-52e5-b827-557766551111"
  }'
```

响应示例：
```json
{
  "session_id": "660e9500-f39c-52e5-b827-557766551111",
  "message_id": "1",
  "response": "Transformer是一种基于注意力机制的神经网络架构...",
  "conversation_history": [
    {
      "role": "user",
      "content": "请解释一下Transformer架构",
      "timestamp": "2024-01-01T12:00:00"
    },
    {
      "role": "assistant",
      "content": "Transformer是一种基于注意力机制的神经网络架构...",
      "timestamp": "2024-01-01T12:00:01"
    }
  ]
}
```

### 3. 发送消息（流式响应）

```bash
curl -X POST "http://localhost:9000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "什么是自然语言处理？",
    "session_id": "660e9500-f39c-52e5-b827-557766551111"
  }'
```

响应（SSE格式）：
```
data: {"session_id":"660e9500-f39c-52e5-b827-557766551111","chunk_id":"1","content":"自","is_last":false}

data: {"session_id":"660e9500-f39c-52e5-b827-557766551111","chunk_id":"2","content":"然","is_last":false}

...

data: {"session_id":"660e9500-f39c-52e5-b827-557766551111","chunk_id":"100","content":"","is_last":true}
```

### 4. 获取会话信息

```bash
curl -X GET "http://localhost:9000/sessions/660e9500-f39c-52e5-b827-557766551111"
```

### 5. 列出所有会话

```bash
curl -X GET "http://localhost:9000/sessions/?user_id=user123&page=1&page_size=10"
```

### 6. 关闭会话

```bash
curl -X POST "http://localhost:9000/sessions/660e9500-f39c-52e5-b827-557766551111/close"
```

### 7. 删除会话

```bash
curl -X DELETE "http://localhost:9000/sessions/660e9500-f39c-52e5-b827-557766551111"
```

---

## 完整使用流程示例

### 场景：基于文档的智能问答

#### 步骤1：上传文档到rag-scheduler

```bash
# 上传技术文档
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@machine_learning_basics.pdf" \
  -F 'metadata={"category": "ML", "level": "beginner"}'
```

获得 `document_id`: `550e8400-e29b-41d4-a716-446655440000`

#### 步骤2：在llm-session创建会话

```bash
curl -X POST "http://localhost:9000/sessions/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "session_name": "ML学习助手"
  }'
```

获得 `session_id`: `660e9500-f39c-52e5-b827-557766551111`

#### 步骤3：查询相关文档

```bash
curl -X POST "http://localhost:8000/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "监督学习和无监督学习的区别",
    "top_k": 3,
    "score_threshold": 0.7
  }'
```

获得相关文档片段和上下文

#### 步骤4：结合上下文进行对话

```bash
curl -X POST "http://localhost:9000/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "请详细解释监督学习和无监督学习的区别",
    "session_id": "660e9500-f39c-52e5-b827-557766551111",
    "context": {
      "context": "从步骤3获得的文档内容..."
    }
  }'
```

---

## Python SDK 示例

### 安装依赖

```bash
pip install httpx
```

### rag-scheduler 客户端

```python
import httpx

class RAGSchedulerClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def upload_document(self, file_path: str, metadata: dict = None):
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f)}
            data = {'metadata': str(metadata)} if metadata else {}
            response = await self.client.post(
                f"{self.base_url}/documents/upload",
                files=files,
                data=data
            )
            return response.json()
    
    async def query(self, query_text: str, top_k: int = 5):
        response = await self.client.post(
            f"{self.base_url}/query/",
            json={"query": query_text, "top_k": top_k}
        )
        return response.json()
    
    async def close(self):
        await self.client.aclose()

# 使用示例
async def main():
    client = RAGSchedulerClient()
    
    # 上传文档
    result = await client.upload_document("document.pdf", {"category": "tech"})
    print(f"Uploaded: {result}")
    
    # 查询
    result = await client.query("什么是深度学习？")
    print(f"Query result: {result}")
    
    await client.close()
```

### llm-session 客户端

```python
import httpx

class LLMSessionClient:
    def __init__(self, base_url="http://localhost:9000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def create_session(self, user_id: str = None, session_name: str = None):
        response = await self.client.post(
            f"{self.base_url}/sessions/",
            json={"user_id": user_id, "session_name": session_name}
        )
        return response.json()
    
    async def send_message(self, message: str, session_id: str = None):
        response = await self.client.post(
            f"{self.base_url}/chat/message",
            json={"message": message, "session_id": session_id}
        )
        return response.json()
    
    async def close(self):
        await self.client.aclose()

# 使用示例
async def main():
    client = LLMSessionClient()
    
    # 创建会话
    result = await client.create_session("user123", "测试会话")
    session_id = result["session_id"]
    print(f"Session created: {session_id}")
    
    # 发送消息
    result = await client.send_message("你好！", session_id)
    print(f"Response: {result['response']}")
    
    await client.close()
```

---

## 错误处理

所有API在出错时都会返回HTTP状态码和错误信息：

```json
{
  "detail": "错误描述信息"
}
```

常见状态码：
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

---

## 更多资源

- rag-scheduler API文档: http://localhost:8000/docs
- llm-session API文档: http://localhost:9000/docs

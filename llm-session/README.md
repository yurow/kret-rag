# KRET-RAG LLM会话管理器

LLM会话管理服务，负责对话管理、上下文维护和模型调用。

## 功能模块

- **会话服务**: 会话创建、查询、管理
- **LLM服务**: 大语言模型调用
- **聊天服务**: 对话流程管理

## API文档

启动服务后访问: http://localhost:9000/docs

## 开发指南

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置环境
```bash
cp .env.example .env
# 编辑 .env 文件填写正确配置（特别是OpenAI API Key）
```

### 启动服务
```bash
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

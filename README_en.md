# KRET-RAG System

A microservices-based RAG (Retrieval-Augmented Generation) system consisting of two core applications:
- **rag-scheduler**: RAG Scheduler - Responsible for document processing, vector retrieval, and knowledge base management
- **llm-session**: LLM Session Manager - Responsible for conversation management, context maintenance, and model invocation

**中文版本**: [README.md](./README.md)

## 📋 Project Status

- **Current Version**: v1.0.0
- **Code Quality Score**: 58/100 ⚠️
- **Issue Tracking**: [View detailed issues and fix plans](./docs/ISSUES_TRACKING.md)
- **Quick Check**: [Daily checklist](./docs/CHECKLIST.md)
- **Completed Fixes**: 1/15 (eval() security vulnerability fixed ✅)

---

## 📚 Documentation Navigation

### Project Documentation
- **[Quick Start](./docs/QUICKSTART.md)** - Environment setup and startup guide
- **[System Architecture](./docs/ARCHITECTURE.md)** - Architecture design and technology selection
- **[API Examples](./docs/API_EXAMPLES.md)** - API usage examples and code snippets
- **[Checklist](./docs/CHECKLIST.md)** - Daily operation checklist
- **[Issue Tracking](./docs/ISSUES_TRACKING.md)** - Known issues and fix plans

### rag-scheduler Service Documentation
- **[Query Test Guide](./rag-scheduler/docs/QUERY_TEST_GUIDE.md)** - Visual test page ⭐
- **[File Processing Flow](./rag-scheduler/docs/FILE_PROCESSING_FLOW.md)** - Document parsing and conversion
- **[Hybrid Search](./rag-scheduler/docs/HYBRID_SEARCH_RERANK.md)** - BM25 + Vector search
- **[Database Guide](./rag-scheduler/docs/DATABASE_GUIDE.md)** - PostgreSQL configuration
- **[Full Documentation Index](./rag-scheduler/docs/README.md)** - All technical documents

### Troubleshooting
- **[Troubleshooting Guide](./rag-scheduler/bugfixes/README.md)** - Common problem solutions

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      KRET-RAG System                        │
├──────────────────────────┬──────────────────────────────────┤
│   rag-scheduler (8000)   │    llm-session (9000)            │
│                          │                                  │
│  ┌────────────────────┐  │  ┌────────────────────────────┐  │
│  │  Document Service  │  │  │   Session Service          │  │
│  ├────────────────────┤  │  ├────────────────────────────┤  │
│  │  Vector Service    │  │  │   LLM Service              │  │
│  ├────────────────────┤  │  ├────────────────────────────┤  │
│  │  RAG Service       │◄─┼──┼──► Chat Service            │  │
│  └────────────────────┘  │  └────────────────────────────┘  │
│                          │                                  │
│  • Document Upload &     │  • Session Creation & Mgmt      │
│    Parsing                │  • Conversation History         │
│  • Text Chunking &       │  • LLM Invocation & Streaming   │
│    Vectorization          │  • Context Management           │
│  • Vector Similarity     │                                  │
│    Search                 │                                  │
│  • Knowledge Base Mgmt    │                                  │
└──────────────────────────┴──────────────────────────────────┘
                           │
                    HTTP API Communication
```

## Features

### rag-scheduler (RAG Scheduler)
- ✅ Multi-format document upload (PDF, DOCX, TXT, MD)
- ✅ Intelligent text chunking
- ✅ Vector storage and retrieval
- ✅ Similarity search
- ✅ Knowledge base management
- ✅ Query rewriting optimization
- ✅ Hybrid search (BM25 + Vector)
- ✅ Rerank reordering
- ✅ Visual test page ⭐

### llm-session (LLM Session Manager)
- ✅ Multi-session management
- ✅ Conversation history maintenance
- ✅ Context awareness
- ✅ LLM integration (OpenAI, Azure, etc.)
- ✅ Streaming response support

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Redis (optional, for caching)

### 2. Install Dependencies

#### rag-scheduler
```bash
cd rag-scheduler
pip install -r requirements.txt
```

#### llm-session
```bash
cd llm-session
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and modify the configuration:

```bash
# rag-scheduler
cp rag-scheduler/.env.example rag-scheduler/.env

# llm-session
cp llm-session/.env.example llm-session/.env
```

**Important**: If you encounter network issues (timeout connecting to huggingface.co), add the following to your `.env` file:
```env
HF_ENDPOINT=https://hf-mirror.com
```

See [Troubleshooting Guide](./rag-scheduler/bugfixes/TROUBLESHOOTING.md) for details.

### 4. Start Services

#### Method 1: Using Startup Scripts (Recommended)
```bash
# Windows
start-scheduler.bat
start-llm-session.bat

# Linux/Mac
./start-scheduler.sh
./start-llm-session.sh
```

#### Method 2: Manual Start
```bash
# Start rag-scheduler
cd rag-scheduler
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start llm-session
cd llm-session
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

### 5. Access API Documentation and Test Pages

- **rag-scheduler API Docs**: http://localhost:8000/docs
- **rag-scheduler Upload Test**: http://localhost:8000/
- **rag-scheduler Query Test**: http://localhost:8000/test-query ⭐ New
- **llm-session API Docs**: http://localhost:9000/docs

## API Endpoints

### rag-scheduler (Port 8000)

#### Document Management
- `POST /documents/upload` - Upload document
- `GET /documents/{document_id}` - Get document information
- `DELETE /documents/{document_id}` - Delete document
- `GET /documents/` - List all documents

#### Query
- `POST /query/` - Query documents and generate answer
- `POST /query/search` - Execute vector search only
- `POST /query/generate` - Complete RAG answer generation

**Test Page**: http://localhost:8000/test-query - Visual testing for all query features ⭐

### llm-session (Port 9000)

#### Session Management
- `POST /sessions/` - Create session
- `GET /sessions/{session_id}` - Get session information
- `DELETE /sessions/{session_id}` - Delete session
- `POST /sessions/{session_id}/close` - Close session
- `GET /sessions/` - List all sessions

#### Chat
- `POST /chat/message` - Send message and get full response
- `POST /chat/stream` - Send message and get streaming response

## Technology Stack

### rag-scheduler
- **Web Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Vector Database**: ChromaDB (extensible to Milvus, Qdrant)
- **Embedding**: Sentence Transformers
- **Document Processing**: PyPDF, python-docx

### llm-session
- **Web Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Cache**: Redis
- **LLM**: OpenAI GPT (extensible to Azure, Claude, etc.)
- **HTTP Client**: HTTPX

## Project Structure

```
kret-rag/
├── rag-scheduler/                # RAG Scheduler
│   ├── app/
│   │   ├── main.py              # Application entry point
│   │   ├── core/                # Core modules
│   │   │   ├── config.py       # Configuration management
│   │   │   └── __init__.py
│   │   ├── models/              # Data models
│   │   │   ├── schemas.py      # Pydantic models
│   │   │   └── __init__.py
│   │   ├── db/                  # Database
│   │   │   ├── database.py     # Database connection
│   │   │   └── __init__.py
│   │   ├── services/            # Business services
│   │   │   ├── document_service.py
│   │   │   ├── vector_service.py
│   │   │   ├── rag_service.py
│   │   │   └── __init__.py
│   │   └── routes/              # API routes
│   │       ├── documents.py
│   │       ├── query.py
│   │       └── __init__.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── llm-session/                  # LLM Session Manager
│   ├── app/
│   │   ├── main.py              # Application entry point
│   │   ├── core/                # Core modules
│   │   │   ├── config.py       # Configuration management
│   │   │   └── __init__.py
│   │   ├── models/              # Data models
│   │   │   ├── schemas.py      # Pydantic models
│   │   │   └── __init__.py
│   │   ├── services/            # Business services
│   │   │   ├── session_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── chat_service.py
│   │   │   └── __init__.py
│   │   └── routes/              # API routes
│   │       ├── sessions.py
│   │       ├── chat.py
│   │       └── __init__.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
└── README.md                     # Project overview
```

## Future Development Plan

### Short-term Optimization
- [ ] Complete database model definitions
- [ ] Implement real LLM calls
- [ ] Add user authentication and authorization
- [ ] Add logging
- [ ] Write unit tests

### Mid-term Expansion
- [ ] Support more vector databases
- [ ] Support more LLM providers
- [ ] Add Rerank mechanism
- [ ] Implement hybrid search
- [ ] Add monitoring and metrics collection

### Long-term Planning
- [ ] Distributed deployment support
- [ ] Load balancing
- [ ] Horizontal scaling capability
- [ ] Multi-tenant support
- [ ] Visual interface

## License

MIT License

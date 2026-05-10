# KRET-RAG 项目问题跟踪与修复计划

> **生成时间**: 2026-05-09  
> **最后更新**: 2026-05-09  
> **状态**: 🔄 进行中  
> **综合评分**: 58/100 ⚠️

---

## 📊 问题概览

| 优先级 | 数量 | 状态 |
|--------|------|------|
| 🔴 高优先级 | 5 | 1/5 已修复 |
| 🟡 中优先级 | 5 | 0/5 待修复 |
| 🟢 低优先级 | 5 | 0/5 待修复 |
| **总计** | **15** | **1/15 已完成** |

---

## 🔴 高优先级问题（立即修复）

### ✅ 问题 1: eval() 安全漏洞 - 已修复

**状态**: ✅ 已完成  
**修复时间**: 2026-05-09  
**位置**: `rag-scheduler/app/routes/documents.py`

#### 问题描述
使用 `eval()` 解析用户输入的 metadata 参数，存在严重的代码注入风险。

#### 原始代码
```python
metadata=eval(metadata) if metadata else None  # ❌ 危险
```

#### 修复方案
```python
import json

# 使用 json.loads 替代 eval()
parsed_metadata = None
if metadata:
    try:
        parsed_metadata = json.loads(metadata)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid metadata format: {str(e)}"
        )
```

#### 验证方法
```bash
# 正常请求测试
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@test.pdf" \
  -F 'metadata={"author": "John"}'

# 攻击尝试（应被阻止）
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@test.pdf" \
  -F 'metadata=__import__("os").system("ls")'
```

---

### 🔴 问题 2: 缺少全局异常处理

**状态**: ⏳ 待修复  
**优先级**: 高  
**影响范围**: 两个应用（rag-scheduler, llm-session）

#### 问题描述
未实现全局异常捕获中间件，导致异常处理不统一，可能泄露敏感信息。

#### 修复位置
- `rag-scheduler/app/main.py`
- `llm-session/app/main.py`

#### 修复方案
```python
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.warning(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

#### 验收标准
- [ ] 所有 HTTP 异常被统一捕获
- [ ] 验证错误返回清晰的错误信息
- [ ] 未处理异常记录日志但不泄露堆栈信息
- [ ] 测试各种异常场景

---

### 🔴 问题 3: 数据库连接池配置缺失

**状态**: ⏳ 待修复  
**优先级**: 高  
**影响范围**: 两个应用的数据库模块

#### 问题描述
SQLAlchemy 引擎未配置连接池，可能导致性能问题和连接泄漏。

#### 修复位置
- `rag-scheduler/app/db/database.py`
- `llm-session/app/db/database.py`

#### 当前代码
```python
from sqlalchemy import create_engine

engine = create_engine(settings.DATABASE_URL)  # ❌ 无连接池配置
```

#### 修复方案
```python
from sqlalchemy import create_engine, pool
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=pool.QueuePool,
    pool_size=10,           # 连接池大小
    max_overflow=20,        # 最大溢出连接数
    pool_timeout=30,        # 获取连接超时时间（秒）
    pool_recycle=1800,      # 连接回收时间（秒）
    pool_pre_ping=True,     # 连接前检测有效性
    echo=False              # 生产环境关闭 SQL 日志
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)
```

#### 配置建议
在 `.env.example` 中添加连接池配置：
```env
# 数据库连接池配置
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800
```

#### 验收标准
- [ ] 连接池正确配置并生效
- [ ] 高并发场景下连接复用正常
- [ ] 无连接泄漏问题
- [ ] 性能监控显示连接池利用率合理

---

### 🔴 问题 4: 敏感信息未加密处理

**状态**: ⏳ 待修复  
**优先级**: 高  
**影响范围**: llm-session 配置和服务

#### 问题描述
API Key 等敏感信息以明文形式存储在配置中，存在泄露风险。

#### 修复位置
- `llm-session/app/core/config.py`
- `llm-session/app/services/llm_service.py`

#### 当前代码
```python
class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""  # ❌ 明文存储
```

#### 修复方案

**步骤 1**: 修改配置类
```python
from pydantic import SecretStr

class Settings(BaseSettings):
    OPENAI_API_KEY: SecretStr = SecretStr("")
    AZURE_API_KEY: SecretStr = SecretStr("")
    
    def get_openai_api_key(self) -> str:
        """获取 OpenAI API Key"""
        return self.OPENAI_API_KEY.get_secret_value()
    
    def get_azure_api_key(self) -> str:
        """获取 Azure API Key"""
        return self.AZURE_API_KEY.get_secret_value()
```

**步骤 2**: 修改服务层使用方式
```python
class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.api_key = settings.get_openai_api_key()  # ✅ 安全获取
        self.model = settings.OPENAI_MODEL
```

**步骤 3**: 更新 `.env.example`
```env
# LLM配置
OPENAI_API_KEY=sk-xxxxxxxxxxxxx  # 提示用户使用真实密钥
AZURE_API_KEY=your-azure-key-here
```

#### 验收标准
- [ ] 所有敏感字段使用 SecretStr 类型
- [ ] 日志中不输出完整密钥
- [ ] API 响应中不包含密钥信息
- [ ] 环境变量文件包含正确的使用说明

---

### 🔴 问题 5: CORS 配置过于宽松

**状态**: ⏳ 待修复  
**优先级**: 高  
**影响范围**: 两个应用的 main.py

#### 问题描述
CORS 允许所有来源访问，存在跨站请求伪造（CSRF）风险。

#### 修复位置
- `rag-scheduler/app/main.py`
- `llm-session/app/main.py`

#### 当前代码
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 修复方案

**步骤 1**: 在配置中添加白名单
```python
# app/core/config.py
class Settings(BaseSettings):
    # ... 其他配置
    
    # CORS 配置
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    ALLOWED_METHODS: str = "GET,POST,PUT,DELETE,PATCH"
    ALLOWED_HEADERS: str = "Content-Type,Authorization"
    
    @property
    def allowed_origins_list(self) -> list:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def allowed_methods_list(self) -> list:
        return [method.strip() for method in self.ALLOWED_METHODS.split(",")]
    
    @property
    def allowed_headers_list(self) -> list:
        return [header.strip() for header in self.ALLOWED_HEADERS.split(",")]
```

**步骤 2**: 更新中间件配置
```python
from app.core.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,  # ✅ 使用白名单
    allow_credentials=True,
    allow_methods=settings.allowed_methods_list,
    allow_headers=settings.allowed_headers_list,
    max_age=3600,  # 预检请求缓存时间
)
```

**步骤 3**: 更新 `.env.example`
```env
# CORS配置
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,https://yourdomain.com
ALLOWED_METHODS=GET,POST,PUT,DELETE,PATCH
ALLOWED_HEADERS=Content-Type,Authorization,X-Requested-With
```

#### 验收标准
- [ ] 仅允许配置的域名访问
- [ ] 非法来源请求被拒绝
- [ ] 预检请求正确处理
- [ ] 生产环境配置正确的域名白名单

---

## 🟡 中优先级问题（本周内修复）

### 🟡 问题 6: 缺少类型注解

**状态**: ⏳ 待修复  
**优先级**: 中  
**影响范围**: 多个路由和服务文件

#### 问题描述
部分函数和方法缺少返回类型注解，降低代码可读性和 IDE 支持。

#### 修复位置
- `rag-scheduler/app/routes/documents.py`
- `rag-scheduler/app/routes/query.py`
- `llm-session/app/routes/sessions.py`
- `llm-session/app/routes/chat.py`

#### 示例修复
```python
# 修复前
async def list_documents(page: int = 1, page_size: int = 10):
    return await document_service.list_documents(page=page, page_size=page_size)

# 修复后
from typing import List

async def list_documents(
    page: int = 1, 
    page_size: int = 10
) -> List[DocumentResponse]:
    """列出所有文档"""
    return await document_service.list_documents(page=page, page_size=page_size)
```

#### 验收标准
- [ ] 所有公共函数都有返回类型注解
- [ ] 复杂类型使用 typing 模块明确标注
- [ ] mypy 类型检查通过

---

### 🟡 问题 7: 缺少 Docstring

**状态**: ⏳ 待修复  
**优先级**: 中  
**影响范围**: 所有服务层和工具类

#### 问题描述
公共方法和类缺少完整的文档字符串，影响代码可维护性。

#### 修复标准
```python
async def upload_document(
    self, 
    file: UploadFile, 
    metadata: Optional[Dict[str, Any]] = None
) -> DocumentResponse:
    """
    上传并处理文档
    
    Args:
        file: 上传的文件对象，支持 PDF/DOCX/TXT/MD 格式
        metadata: 可选的元数据字典，包含作者、分类等信息
        
    Returns:
        DocumentResponse: 包含文档ID和状态的响应对象
        
    Raises:
        ValueError: 当文件格式不支持或大小超过限制时
        HTTPException: 当文件保存失败时（500错误）
        
    Example:
        >>> result = await service.upload_document(file, {"author": "John"})
        >>> print(result.document_id)
    """
```

#### 验收标准
- [ ] 所有公共类有类级别 docstring
- [ ] 所有公共方法有完整的参数、返回值、异常说明
- [ ] 复杂算法包含实现思路注释

---

### 🟡 问题 8: 内存存储而非持久化

**状态**: ⏳ 待修复  
**优先级**: 中  
**影响范围**: `llm-session/app/services/session_service.py`

#### 问题描述
会话数据存储在内存中，服务重启后数据丢失，无法支持分布式部署。

#### 当前代码
```python
class SessionService:
    def __init__(self):
        self.sessions: Dict[str, SessionInfo] = {}  # ❌ 内存存储
        self.contexts: Dict[str, ConversationContext] = {}
```

#### 修复方案

**选项 1**: 使用 Redis（推荐）
```python
import redis
import json
from app.core.config import settings

class SessionService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.session_ttl = settings.SESSION_TTL
    
    async def create_session(self, request: CreateSessionRequest) -> SessionInfo:
        session_id = str(uuid.uuid4())
        session_info = SessionInfo(...)
        
        # 存储到 Redis
        self.redis_client.setex(
            f"session:{session_id}",
            self.session_ttl,
            json.dumps(session_info.dict(), default=str)
        )
        
        return session_info
    
    async def get_session(self, session_id: str) -> Optional[SessionInfo]:
        data = self.redis_client.get(f"session:{session_id}")
        if not data:
            return None
        return SessionInfo(**json.loads(data))
```

**选项 2**: 使用数据库
```python
from sqlalchemy.orm import Session
from app.db.database import get_db

class SessionService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_session(self, request: CreateSessionRequest) -> SessionInfo:
        # 使用 SQLAlchemy 模型存储
        session_model = SessionModel(...)
        self.db.add(session_model)
        self.db.commit()
        return session_model.to_response()
```

#### 验收标准
- [ ] 会话数据持久化存储
- [ ] 服务重启后数据不丢失
- [ ] 支持多实例部署
- [ ] 会话过期自动清理

---

### 🟡 问题 9: 缺少日志记录

**状态**: ⏳ 待修复  
**优先级**: 中  
**影响范围**: 所有服务层代码

#### 问题描述
未使用标准 logging 模块，无法追踪系统运行状态和排查问题。

#### 修复方案

**步骤 1**: 配置日志
```python
# app/core/logging_config.py
import logging
import sys
from app.core.config import settings

def setup_logging():
    """配置日志系统"""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    # 根日志器配置
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)
    
    # 文件处理器（可选）
    if settings.LOG_FILE:
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
```

**步骤 2**: 在服务中使用
```python
import logging

logger = logging.getLogger(__name__)

class DocumentService:
    async def upload_document(self, file: UploadFile, metadata=None):
        logger.info(f"Uploading document: {file.filename}, size: {file.size}")
        
        try:
            # 业务逻辑
            result = await self._process_document(file)
            logger.info(f"Document uploaded successfully: {result.document_id}")
            return result
        except ValueError as e:
            logger.warning(f"Validation failed for {file.filename}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to upload document {file.filename}: {str(e)}", exc_info=True)
            raise
```

**步骤 3**: 在配置中添加
```env
# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/var/log/kret-rag/app.log
DEBUG=false
```

#### 验收标准
- [ ] 关键操作有 INFO 级别日志
- [ ] 错误和异常有 ERROR 级别日志并包含堆栈信息
- [ ] 敏感信息不在日志中输出
- [ ] 日志格式统一且包含时间戳

---

### 🟡 问题 10: TODO 标记过多

**状态**: ⏳ 待修复  
**优先级**: 中  
**统计**: 16+ 个 TODO 标记

#### 问题分布
- `document_service.py`: 7 个 TODO
- `vector_service.py`: 6 个 TODO
- `llm_service.py`: 3 个 TODO

#### 修复策略

**优先级排序**:
1. P0: 实现真实的 LLM 调用（影响核心功能）
2. P1: 完成向量数据库集成（影响检索功能）
3. P2: 实现文档文本提取（影响上传功能）
4. P3: 完善数据库模型定义

#### 行动计划
```markdown
## Week 1: 核心功能实现
- [ ] 实现 OpenAI API 调用
- [ ] 实现 ChromaDB 向量存储
- [ ] 实现 PDF 文本提取

## Week 2: 辅助功能完善
- [ ] 实现 DOCX 文本提取
- [ ] 完善数据库模型
- [ ] 添加 RAG 检索逻辑

## Week 3: 优化与测试
- [ ] 移除所有 TODO 标记
- [ ] 编写集成测试
- [ ] 性能优化
```

#### 验收标准
- [ ] 所有 TODO 要么实现，要么转化为 Issue
- [ ] 核心功能完整可用
- [ ] 代码中无悬空的 TODO 注释

---

## 🟢 低优先级问题（本月内修复）

### 🟢 问题 11: 依赖版本锁定过于严格

**状态**: ⏳ 待修复  
**优先级**: 低  

#### 建议
```txt
# 修复前
fastapi==0.104.1

# 修复后
fastapi>=0.104.0,<0.110.0
uvicorn>=0.24.0,<0.30.0
pydantic>=2.5.0,<3.0.0
```

---

### 🟢 问题 12: 缺少 .gitignore 文件

**状态**: ⏳ 待修复  
**优先级**: 低  

#### 修复方案
创建项目根目录的 `.gitignore`:
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
dist/
build/
*.egg

# Virtual Environment
.venv/
venv/
ENV/

# Environment Variables
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Database
*.db
*.sqlite3
*.sqlite

# Logs
*.log
logs/

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
```

---

### 🟢 问题 13: 缺少单元测试

**状态**: ⏳ 待修复  
**优先级**: 低  
**目标覆盖率**: 80%

#### 测试结构
```
rag-scheduler/
└── tests/
    ├── conftest.py          # 测试配置和fixtures
    ├── test_documents.py    # 文档服务测试
    ├── test_vectors.py      # 向量服务测试
    ├── test_rag.py          # RAG服务测试
    └── test_routes/
        ├── test_documents.py
        └── test_query.py

llm-session/
└── tests/
    ├── conftest.py
    ├── test_sessions.py
    ├── test_llm.py
    ├── test_chat.py
    └── test_routes/
        ├── test_sessions.py
        └── test_chat.py
```

#### 示例测试
```python
# tests/test_documents.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_document_success():
    """测试文档上传成功场景"""
    with open("test.pdf", "rb") as f:
        response = client.post(
            "/documents/upload",
            files={"file": ("test.pdf", f, "application/pdf")},
            data={"metadata": '{"author": "Test"}'}
        )
    assert response.status_code == 200
    assert "document_id" in response.json()

def test_upload_document_invalid_format():
    """测试不支持的文件格式"""
    with open("test.exe", "rb") as f:
        response = client.post(
            "/documents/upload",
            files={"file": ("test.exe", f, "application/octet-stream")}
        )
    assert response.status_code == 400
```

#### 验收标准
- [ ] 核心服务单元测试覆盖率 ≥ 80%
- [ ] API 路由测试覆盖率 ≥ 90%
- [ ] 所有测试用例通过
- [ ] CI/CD 集成自动化测试

---

### 🟢 问题 14: 代码复杂度较高

**状态**: ⏳ 待修复  
**优先级**: 低  

#### 问题文件
- `document_service.py`: 148 行
- `session_service.py`: 154 行

#### 重构建议
将大方法拆分为小的辅助方法，单个方法不超过 50 行：

```python
# 重构前
async def upload_document(self, file: UploadFile, metadata=None):
    # 100+ 行代码混合验证、处理、存储逻辑
    pass

# 重构后
async def upload_document(self, file: UploadFile, metadata=None):
    """上传文档的主流程"""
    self._validate_file(file)
    document_id = self._generate_document_id()
    await self._save_document(file, document_id)
    return await self._create_document_record(document_id, file, metadata)

def _validate_file(self, file: UploadFile):
    """验证文件格式和大小"""
    if file.size and file.size > settings.MAX_DOCUMENT_SIZE:
        raise ValueError(f"File size exceeds limit")
    
    extension = file.filename.split('.')[-1].lower()
    if extension not in settings.SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {extension}")

async def _save_document(self, file: UploadFile, document_id: str):
    """保存文档到存储"""
    # 具体实现
    pass
```

---

### 🟢 问题 15: 缺少性能优化

**状态**: ⏳ 待修复  
**优先级**: 低  

#### 优化点
1. **向量搜索缓存**: 使用 Redis 缓存频繁查询
2. **异步任务队列**: 文档处理使用 Celery/RQ
3. **数据库查询优化**: 添加索引，使用 selectinload
4. **响应压缩**: 启用 gzip 压缩

#### 实施计划
```python
# 向量搜索缓存示例
import hashlib
import json

class VectorStoreService:
    async def similarity_search(self, query: str, top_k: int = 5):
        # 生成缓存键
        cache_key = f"search:{hashlib.md5(query.encode()).hexdigest()}:{top_k}"
        
        # 尝试从缓存获取
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # 执行搜索
        results = await self._perform_search(query, top_k)
        
        # 缓存结果（5分钟过期）
        self.redis_client.setex(
            cache_key, 
            300, 
            json.dumps(results, default=str)
        )
        
        return results
```

---

## 📅 修复时间表

### 第一阶段：安全加固（第 1-2 天）
- [x] ✅ 修复 eval() 安全漏洞
- [ ] 添加全局异常处理
- [ ] 配置数据库连接池
- [ ] 使用 SecretStr 保护敏感信息
- [ ] 配置 CORS 白名单

### 第二阶段：代码质量提升（第 3-5 天）
- [ ] 完善类型注解
- [ ] 添加 Docstring
- [ ] 实现 Redis 会话持久化
- [ ] 添加日志记录系统
- [ ] 处理 TODO 标记（P0/P1）

### 第三阶段：功能完善（第 6-10 天）
- [ ] 实现真实 LLM 调用
- [ ] 完成向量数据库集成
- [ ] 实现文档文本提取
- [ ] 完善数据库模型
- [ ] 处理剩余 TODO

### 第四阶段：测试与优化（第 11-15 天）
- [ ] 编写单元测试
- [ ] 性能优化
- [ ] 代码重构
- [ ] 创建 .gitignore
- [ ] 调整依赖版本

---

## 🎯 验收标准

### 安全性
- [ ] 无 eval/exec 等危险函数使用
- [ ] 所有敏感信息加密存储
- [ ] CORS 配置合理的白名单
- [ ] 输入验证完整
- [ ] SQL 注入防护到位

### 代码质量
- [ ] 所有公共 API 有类型注解
- [ ] 所有公共方法有 Docstring
- [ ] 代码复杂度（Cyclomatic）≤ 10
- [ ] 单个方法行数 ≤ 50
- [ ] 单个类行数 ≤ 200

### 可靠性
- [ ] 全局异常处理完善
- [ ] 日志记录完整
- [ ] 数据库连接池配置正确
- [ ] 会话数据持久化
- [ ] 无内存泄漏

### 可测试性
- [ ] 单元测试覆盖率 ≥ 80%
- [ ] API 测试覆盖率 ≥ 90%
- [ ] 所有测试用例通过
- [ ] CI/CD 集成完成

### 性能
- [ ] 关键接口响应时间 ≤ 200ms
- [ ] 向量搜索有缓存机制
- [ ] 数据库查询有索引优化
- [ ] 支持水平扩展

---

## 📝 变更记录

| 日期 | 版本 | 变更内容 | 负责人 |
|------|------|----------|--------|
| 2026-05-09 | 1.0 | 初始版本，识别 15 个问题 | AI Assistant |
| 2026-05-09 | 1.1 | 修复 eval() 安全漏洞 | AI Assistant |

---

## 🔗 相关资源

- [FastAPI 最佳实践](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy 连接池配置](https://docs.sqlalchemy.org/en/20/core/pooling.html)
- [Pydantic SecretStr 文档](https://docs.pydantic.dev/latest/api/types/#pydantic.types.SecretStr)
- [Python Logging 指南](https://docs.python.org/3/howto/logging.html)
- [pytest 测试框架](https://docs.pytest.org/en/stable/)

---

**最后更新**: 2026-05-09  
**下次审查**: 2026-05-16  
**项目状态**: 🔄 持续改进中

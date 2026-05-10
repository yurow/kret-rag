@echo off
chcp 65001 >nul
echo ========================================
echo  Starting KRET-RAG Scheduler
echo ========================================
echo.

REM Change to rag-scheduler directory
cd /d "%~dp0rag-scheduler"

if not exist .env (
    echo WARNING: .env file not found, using example configuration
    echo Please copy .env.example to .env and configure it properly
    echo.
)

REM Set TensorFlow oneDNN environment variable (disable to avoid warnings)
set TF_ENABLE_ONEDNN_OPTS=0

echo Current directory: %CD%
echo.
echo Starting RAG Scheduler on port 8000...
echo.
echo API Documentation: http://localhost:8000/docs
echo Upload Test Page: http://localhost:8000/
echo Query Test Page: http://localhost:8000/test-query
echo.

REM Start uvicorn from the correct directory
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
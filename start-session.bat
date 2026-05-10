@echo off
echo ========================================
echo  Starting KRET-RAG LLM Session Manager
echo ========================================
echo.

cd llm-session

if not exist .env (
    echo WARNING: .env file not found, using example configuration
    echo Please copy .env.example to .env and configure it properly
    echo.
)

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting LLM Session Manager on port 9000...
echo Access API docs at: http://localhost:9000/docs
echo.

uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload

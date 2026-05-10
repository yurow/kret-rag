@echo off
chcp 65001 >nul
echo ========================================
echo   KRET-RAG 文档上传测试环境启动
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/3] 检查依赖包...
pip list | findstr "fastapi" >nul
if errorlevel 1 (
    echo [提示] 正在安装依赖包...
    pip install -r requirements.txt
) else (
    echo [完成] 依赖包已安装
)

echo.
echo [2/3] 创建上传目录...
if not exist "uploads" mkdir uploads
echo [完成] 上传目录就绪

echo.
echo [3/3] 启动 RAG Scheduler 服务...
echo.
echo ========================================
echo   服务地址: http://localhost:8000
echo   API文档:  http://localhost:8000/docs
echo   测试页面: rag-scheduler\upload_test.html
echo ========================================
echo.
echo 按 Ctrl+C 停止服务
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

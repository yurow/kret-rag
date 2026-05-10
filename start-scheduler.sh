#!/bin/bash

echo "========================================"
echo " Starting KRET-RAG Scheduler"
echo "========================================"
echo ""

cd rag-scheduler

if [ ! -f .env ]; then
    echo "WARNING: .env file not found, using example configuration"
    echo "Please copy .env.example to .env and configure it properly"
    echo ""
fi

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Starting RAG Scheduler on port 8000..."
echo "Access API docs at: http://localhost:8000/docs"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

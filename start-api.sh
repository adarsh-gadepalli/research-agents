#!/bin/bash
# Helper script to start FastAPI server
# Tries python3 first, then python, then py

cd src

if command -v python3 &> /dev/null; then
    echo "Using python3"
    python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
elif command -v python &> /dev/null; then
    echo "Using python"
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
elif command -v py &> /dev/null; then
    echo "Using py"
    py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
else
    echo "Error: No Python interpreter found. Please install Python 3.8+"
    exit 1
fi


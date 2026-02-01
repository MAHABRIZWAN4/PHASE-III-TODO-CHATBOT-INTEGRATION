#!/bin/bash
echo "Starting backend with debug logs..."
source .venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

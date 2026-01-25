#!/bin/bash

# Start Backend and Frontend for Testing

echo "=========================================="
echo "Starting Backend and Frontend Servers"
echo "=========================================="
echo ""

# Check if already running
if lsof -i :8001 > /dev/null 2>&1; then
    echo "⚠ Backend already running on port 8001"
else
    echo "Starting Backend on port 8001..."
    cd /mnt/d/new/Phase-III/backend
    source .venv/bin/activate
    uvicorn main:app --reload --port 8001 > backend.log 2>&1 &
    BACKEND_PID=$!
    echo "✓ Backend started (PID: $BACKEND_PID)"
    echo "  Logs: backend/backend.log"
fi

echo ""

if lsof -i :3000 > /dev/null 2>&1; then
    echo "⚠ Frontend already running on port 3000"
else
    echo "Starting Frontend on port 3000..."
    cd /mnt/d/new/Phase-III/frontend
    npm run dev > frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "✓ Frontend started (PID: $FRONTEND_PID)"
    echo "  Logs: frontend/frontend.log"
fi

echo ""
echo "=========================================="
echo "Waiting for servers to start..."
echo "=========================================="
sleep 5

# Check if servers are responding
echo ""
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✓ Backend is responding: http://localhost:8001"
else
    echo "✗ Backend not responding on port 8001"
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "✓ Frontend is responding: http://localhost:3000"
else
    echo "✗ Frontend not responding on port 3000"
fi

echo ""
echo "=========================================="
echo "Ready for Testing!"
echo "=========================================="
echo ""
echo "1. Open: http://localhost:3000/chat"
echo "2. Press F12 (DevTools)"
echo "3. Send: 'Add task to buy groceries'"
echo "4. Answer questions in structured format"
echo "5. Check console logs"
echo "6. Go to: http://localhost:3000/dashboard"
echo ""
echo "To stop servers:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""

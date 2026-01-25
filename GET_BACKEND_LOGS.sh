#!/bin/bash

echo "════════════════════════════════════════════════════════════════════════════"
echo "                    Backend Debug Log Collector"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

# Find uvicorn process
UVICORN_PID=$(ps aux | grep "uvicorn main:app" | grep -v grep | awk '{print $2}' | head -1)

if [ -z "$UVICORN_PID" ]; then
    echo "❌ Backend is NOT running!"
    echo ""
    echo "Please start the backend:"
    echo "  cd /mnt/d/new/Phase-III/backend"
    echo "  source .venv/bin/activate"
    echo "  uvicorn main:app --reload --port 8001"
    echo ""
    exit 1
fi

echo "✓ Backend is running (PID: $UVICORN_PID)"
echo ""

# Check if backend is responding
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✓ Backend is responding on port 8001"
else
    echo "❌ Backend is NOT responding on port 8001"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "                    Testing Backend with Debug Logs"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

# Create a test log file
LOG_FILE="/tmp/backend_test_$(date +%s).log"

echo "📝 Logs will be saved to: $LOG_FILE"
echo ""
echo "Now, please do the following:"
echo ""
echo "1. Open your browser: http://localhost:3000/chat"
echo "2. Send this message: 'Add task to buy groceries'"
echo "3. Wait 5 seconds"
echo "4. Come back here and press ENTER"
echo ""
read -p "Press ENTER after sending the message..."

echo ""
echo "Checking backend terminal for [DEBUG] logs..."
echo ""

# Try to find the terminal output
# This won't work if backend is in a different terminal, but we can check the process
echo "Backend process info:"
ps -fp $UVICORN_PID

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo "⚠️  IMPORTANT: I cannot automatically capture terminal output."
echo ""
echo "Please do this manually:"
echo ""
echo "1. Find the terminal window where you ran 'uvicorn main:app --reload'"
echo "2. Look for lines starting with [DEBUG]"
echo "3. Copy ALL the [DEBUG] lines"
echo "4. Paste them in your response to me"
echo ""
echo "If you don't see ANY [DEBUG] lines:"
echo "  - The backend might not have reloaded"
echo "  - Press Ctrl+C in that terminal"
echo "  - Run: uvicorn main:app --reload --port 8001"
echo "  - Try sending the message again"
echo ""
echo "════════════════════════════════════════════════════════════════════════════"


#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting AnalyticBot...${NC}"

# Function to kill processes on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down servers...${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit
}

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

# Start Backend
echo -e "${GREEN}Starting Backend Server (FastAPI)...${NC}"
# Ensure we are in the project root
cd "$(dirname "$0")"

# Check if venv exists
if [ -d "venv" ]; then
    PYTHON_CMD="./venv/bin/python"
else
    echo "Warning: venv not found, trying system python..."
    if ! command -v python &> /dev/null; then
        if command -v python3 &> /dev/null; then
            PYTHON_CMD=python3
        else
            echo "Error: Python not found"
            exit 1
        fi
    else
        PYTHON_CMD=python
    fi
fi

$PYTHON_CMD backend/main.py &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 2

# Start Frontend
echo -e "${GREEN}Starting Frontend Server (Vite)...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!

# Wait for both processes to keep script running
wait

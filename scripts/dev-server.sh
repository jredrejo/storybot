#!/bin/bash
#
# StoryBot Development Server
#
# Quick script to start the development server with auto-reload.
# This is for development on x86_64 machines, not for production Jetson.
#
set -e

# Change to project root
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [[ ! -d ".venv" ]]; then
    echo "Virtual environment not found. Creating..."
    uv venv
    echo "Installing dependencies..."
    uv sync --extra dev
fi

echo "Starting StoryBot development server..."
echo "API will be available at http://localhost:8000"
echo "API docs at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start uvicorn with reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

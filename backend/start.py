#!/usr/bin/env python3
"""
Start script for AI Action Agent Backend
Runs the FastAPI server with uvicorn
"""
import uvicorn
import os
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

# Load .env from the backend directory
env_file = Path(__file__).parent / ".env"
load_dotenv(env_file)

# Verify GROQ_API_KEY is set
if not os.getenv("GROQ_API_KEY"):
    print("⚠️  WARNING: GROQ_API_KEY not set in .env file")
    print("You can set it with: $env:GROQ_API_KEY='your-api-key'")

# Get port from environment or use default
port = int(os.getenv("PORT", 8000))
host = os.getenv("HOST", "0.0.0.0")

if __name__ == "__main__":
    print("🚀 Starting AI Action Agent Backend...")
    print(f"📡 Server will run on http://{host}:{port}")
    print(f"📚 API docs available at http://localhost:{port}/docs")
    print("\nPress Ctrl+C to stop the server\n")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

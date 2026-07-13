from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback
import json
import os

# Check for required environment variables
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("⚠️  WARNING: GROQ_API_KEY is not set!")
    print("The backend will fail when trying to process commands.")
else:
    print("✅ GROQ_API_KEY is configured")

# Import after environment checks
try:
    from agent.planner import plan_task
    from agent.executer import execute_plan
    print("✅ Agent modules imported successfully")
except Exception as e:
    print(f"❌ Error importing agent modules: {e}")
    import traceback
    traceback.print_exc()

app = FastAPI(title="AI Action Agent", version="1.0.0")

# Add CORS middleware FIRST (before all routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Command(BaseModel):
    command: str


# Global exception handler to catch ALL exceptions and return JSON
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_details = {
        "logs": [
            f"❌ Backend Error: {type(exc).__name__}",
            str(exc),
            traceback.format_exc()
        ],
        "plan": None,
        "results": [],
        "error": str(exc),
        "type": type(exc).__name__
    }
    print(f"\n=== EXCEPTION ===")
    print(f"Type: {type(exc).__name__}")
    print(f"Message: {str(exc)}")
    print(traceback.format_exc())
    print(f"=================\n")

    return JSONResponse(
        status_code=500,
        content=error_details,
    )


@app.get("/")
def root():
    return {
        "name": "AI Action Agent Backend",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "run": "/run (POST)",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "message": "Backend is running",
        "groq_configured": bool(groq_api_key)
        print(msg)  # Also print to server logs

    try:
        # Validate API key
        if not os.getenv("GROQ_API_KEY"):
            raise ValueError("GROQ_API_KEY environment variable is not set")

        log(f"🤖 Received command: {cmd.command}")

        plan = plan_task(cmd.command)

        if not plan or "steps" not in plan:
            raise ValueError("Invalid plan returned from AI")

            "plan": plan,
            "results": extracted_data,
            "success": True
        }

        # Ensure response is JSON serializable
        return json.loads(json.dumps(response, default=str))

    except ValueError as e:
        error_msg = f"❌ Validation Error: {str(e)}"
        log(error_msg)
        return {
            "logs": logs,
            "plan": None,
            "results": [],
            "error": str(e),
            "success": False
        }
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        log(error_msg)
        log(traceback.format_exc())
        print(f"\n=== EXCEPTION IN /run ===")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print(traceback.format_exc())
        print(f"========================\n")

        return {
            "logs": logs,
            "plan": None,
            "results": [],
            "error": str(e),
            "type": type(e).__name__,
            "success": False
        }

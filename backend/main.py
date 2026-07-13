from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback
import json

from agent.planner import plan_task
from agent.executer import execute_plan

app = FastAPI()

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
            f"❌ Backend Error: {str(exc)}",
            "Traceback:",
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


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running"}


@app.post("/run")
def run_agent(cmd: Command):
    logs = []

    def log(msg):
        logs.append(msg)
        print(msg)  # Also print to server logs

    try:
        log(f"🤖 Received command: {cmd.command}")

        plan = plan_task(cmd.command)
        log(f"✅ Plan created with {len(plan.get('steps', []))} steps")

        extracted_data = execute_plan(plan, log)

        response = {
            "logs": logs,
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

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback
import os

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


# Global exception handler to return JSON for all errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "logs": [f"❌ Error: {str(exc)}", traceback.format_exc()],
            "plan": None,
            "results": [],
            "error": str(exc)
        },
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/run")
def run_agent(cmd: Command):
    logs = []

    def log(msg):
        logs.append(msg)

    try:
        plan = plan_task(cmd.command)
        log(f"✅ Plan created with {len(plan['steps'])} steps")
        extracted_data = execute_plan(plan, log)
        return {"logs": logs, "plan": plan, "results": extracted_data}
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logs.append(error_msg)
        logs.append(traceback.format_exc())
        return {"logs": logs, "plan": None, "results": [], "error": str(e)}

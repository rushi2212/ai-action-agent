from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.planner import plan_task
from agent.executer import execute_plan

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class Command(BaseModel):
    command: str

@app.post("/run")
def run_agent(cmd: Command):
    logs = []

    def log(msg):
        logs.append(msg)

    plan = plan_task(cmd.command)
    log(f"✅ Plan created with {len(plan['steps'])} steps")
    extracted_data = execute_plan(plan, log)

    return {"logs": logs, "plan": plan, "results": extracted_data}

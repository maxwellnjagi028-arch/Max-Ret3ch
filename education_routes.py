from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database import get_db

router = APIRouter(prefix="/api/tutorials", tags=["education"])

class EnrollPayload(BaseModel):
    user_name: Optional[str] = "Student"
    user_email: Optional[str] = "student@example.com"

class ExecuteCodePayload(BaseModel):
    tutorial_id: int
    code: str

@router.get("")
def list_tutorials(category: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    if category:
        cursor.execute("SELECT id, title, category, level, duration_minutes, description, enrolled_count FROM tutorials WHERE category = ?", (category,))
    else:
        cursor.execute("SELECT id, title, category, level, duration_minutes, description, enrolled_count FROM tutorials")
    rows = cursor.fetchall()
    conn.close()
    return {"tutorials": [dict(r) for r in rows]}

@router.get("/{tutorial_id}")
def get_tutorial_detail(tutorial_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tutorials WHERE id = ?", (tutorial_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Tutorial not found")
    return {"tutorial": dict(row)}

@router.post("/{tutorial_id}/enroll")
def enroll_tutorial(tutorial_id: int, payload: EnrollPayload):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tutorials SET enrolled_count = enrolled_count + 1 WHERE id = ?", (tutorial_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"Successfully enrolled in course #{tutorial_id}!"}

@router.post("/execute-sandbox")
def run_sandbox_code(payload: ExecuteCodePayload):
    # Safe simulation of Ted's intelligent code evaluator
    code = payload.code.strip()
    simulated_output = ""
    lint_tips = []

    if "AgentTool" in code or "tools" in code:
        simulated_output = ">> Initializing Autonomous Agent Cluster...\n>> Registering tools: [ping, server_triage]\n>> Decision policy: Zero-Shot React with Human-in-the-Loop\n>> Tool 'ping' executed on nexus.maxret3ch.ai: {status: 'ONLINE', latency: 14.2ms}\n>> Agent task successfully solved with 0 errors."
        lint_tips.append("✓ Clean tool definition schema detected.")
        lint_tips.append("✓ Safe execution boundary verified.")
    elif "WebSocket" in code or "FastAPI" in code or "telemetry" in code:
        simulated_output = ">> Starting Uvicorn ASGI Server on port 8000...\n>> WebSocket client connected: 127.0.0.1:51240\n>> Streaming telemetry packet #1: {cpu_pct: 34, temp_c: 52.4}\n>> Streaming telemetry packet #2: {cpu_pct: 38, temp_c: 53.1}\n>> WebSocket heartbeat acknowledged (Ping 4ms)."
        lint_tips.append("✓ Async event loop handles concurrent connections safely.")
    elif "diagnose_rail" in code or "12V" in code or "resistance" in code:
        simulated_output = ">> Hardware Multimeter Bridge Connected\n>> Probing 12V_MAIN rail: 1.2 Ohms detected.\n>> Result: CRITICAL SHORT DETECTED: Do NOT apply full voltage! Use 1V current injection.\n>> Thermal IR camera triggered: ceramic cap C842 glowing at 58°C."
        lint_tips.append("✓ Power rail safety rule verified before high current injection.")
    else:
        simulated_output = f">> Simulated Python 3.14 Execution Environment\n>> Running script ({len(code)} characters)...\n>> Execution completed successfully (returncode 0)."
        lint_tips.append("✓ Code parsed with no syntax faults.")

    return {
        "success": True,
        "output": simulated_output,
        "ted_feedback": "Ted AI Code Review: Excellent implementation adhering to MaxReT3ch design patterns.",
        "tips": lint_tips
    }

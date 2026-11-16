from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
from app.ted_brain import ted_engine
from app.database import get_db
from app.auth import require_staff_or_admin

router = APIRouter(prefix="/api/ted", tags=["ted"])

class ChatPayload(BaseModel):
    message: str
    session_id: Optional[str] = None
    visitor_name: Optional[str] = "Visitor"
    visitor_email: Optional[str] = None

class ScopeProposalPayload(BaseModel):
    client_name: str
    client_email: str
    client_company: Optional[str] = ""
    vertical: str
    project_description: str
    budget: Optional[float] = None
    timeline: Optional[str] = None

class TroubleshootPayload(BaseModel):
    issue_description: str
    device_model: Optional[str] = "Desktop/Laptop"

class MarketingPayload(BaseModel):
    title: str
    audience: str
    channel: str # linkedin, email, twitter, blog

@router.post("/chat")
def chat_with_ted(payload: ChatPayload):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    result = ted_engine.chat(
        user_message=payload.message,
        session_id=payload.session_id,
        visitor_name=payload.visitor_name,
        visitor_email=payload.visitor_email
    )
    return result

@router.post("/propose")
def create_project_proposal(payload: ScopeProposalPayload):
    proposal = ted_engine.generate_automated_proposal(
        client_name=payload.client_name,
        client_email=payload.client_email,
        client_company=payload.client_company,
        text=f"{payload.vertical} - {payload.project_description}"
    )
    return {
        "success": True,
        "message": "Quotation structured and routed to Executive Human Approval Queue.",
        "proposal": proposal
    }

@router.post("/troubleshoot")
def troubleshoot_device(payload: TroubleshootPayload):
    diag = ted_engine.process_troubleshooting(payload.issue_description)
    return {
        "success": True,
        "device_model": payload.device_model,
        "diagnostic": diag
    }

@router.get("/report")
def get_executive_report():
    report = ted_engine.generate_business_report()
    return {"success": True, "report": report}

@router.post("/marketing")
def generate_marketing(payload: MarketingPayload):
    camp = ted_engine.generate_marketing_campaign(
        title=payload.title,
        audience=payload.audience,
        channel=payload.channel
    )
    return {"success": True, "campaign": camp}

@router.get("/interactions")
def get_interactions(request: Request):
    require_staff_or_admin(request)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, session_id, visitor_name, visitor_email, messages_count, summary, sentiment, primary_intent, action_items_json, transcript_json, created_at
    FROM ted_interactions
    ORDER BY id DESC
    LIMIT 50
    """)
    rows = cursor.fetchall()
    conn.close()

    interactions = []
    for r in rows:
        item = dict(r)
        try:
            item["action_items"] = json.loads(item["action_items_json"]) if item["action_items_json"] else []
        except Exception:
            item["action_items"] = []
        try:
            item["transcript"] = json.loads(item["transcript_json"]) if item["transcript_json"] else []
        except Exception:
            item["transcript"] = []
        interactions.append(item)

    return {"interactions": interactions}

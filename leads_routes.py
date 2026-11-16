from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from app.database import get_db
from app.auth import require_staff_or_admin

router = APIRouter(prefix="/api/leads", tags=["leads"])

class LeadCreatePayload(BaseModel):
    name: str
    email: str
    phone: Optional[str] = ""
    company: Optional[str] = ""
    vertical_interest: str
    requirements_summary: str
    estimated_budget: Optional[float] = 5000.0
    timeline: Optional[str] = "Within 30 days"
    score: Optional[str] = "warm"

class LeadStatusPayload(BaseModel):
    status: str
    score: Optional[str] = None
    notes: Optional[str] = None

@router.get("")
def list_leads(request: Request, status: Optional[str] = None, score: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM leads WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if score:
        query += " AND score = ?"
        params.append(score)
    query += " ORDER BY id DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return {"leads": [dict(r) for r in rows]}

@router.post("")
def capture_lead(payload: LeadCreatePayload):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    # Determine lead score
    score = payload.score or "warm"
    if (payload.estimated_budget and payload.estimated_budget >= 300000) or (payload.timeline and "immediate" in payload.timeline.lower()):
        score = "hot"

    cursor.execute("""
    INSERT INTO leads (name, email, phone, company, vertical_interest, requirements_summary, estimated_budget, timeline, score, status, captured_by, ai_confidence, notes, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', 'web_form', 0.94, 'Inbound lead via portal form', ?, ?)
    """, (
        payload.name.strip(), payload.email.strip(), payload.phone.strip(), payload.company.strip(),
        payload.vertical_interest, payload.requirements_summary.strip(), payload.estimated_budget,
        payload.timeline, score, now, now
    ))
    lead_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {"success": True, "lead_id": lead_id, "score": score, "message": "Lead captured successfully!"}

@router.put("/{lead_id}/status")
def update_lead_status(lead_id: int, payload: LeadStatusPayload, request: Request):
    require_staff_or_admin(request)
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    updates = ["status = ?", "updated_at = ?"]
    params = [payload.status, now]

    if payload.score:
        updates.append("score = ?")
        params.append(payload.score)
    if payload.notes:
        updates.append("notes = ?")
        params.append(payload.notes)

    params.append(lead_id)
    query = f"UPDATE leads SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, params)
    conn.commit()
    conn.close()

    return {"success": True, "message": f"Lead {lead_id} updated to {payload.status}"}

@router.delete("/{lead_id}")
def delete_lead(lead_id: int, request: Request):
    require_staff_or_admin(request)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Lead deleted"}

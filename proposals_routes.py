from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import json
from app.database import get_db
from app.auth import require_staff_or_admin, require_admin, get_current_user_from_request

router = APIRouter(prefix="/api/proposals", tags=["proposals"])

class ApprovePayload(BaseModel):
    decision: str # "approved" or "rejected"
    approval_notes: Optional[str] = "Approved by executive leadership."

class CustomProposalPayload(BaseModel):
    client_name: str
    client_email: str
    client_company: Optional[str] = None
    project_title: str
    vertical: str
    scope_details: str
    itemized_costs: List[Dict[str, Any]]
    subtotal: float
    discount: float = 0.0
    tax: float = 0.0
    total_amount: float
    estimated_days: int
    ted_summary: Optional[str] = "Manual draft approved for client submission."

@router.get("")
def list_proposals(status_filter: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    if status_filter:
        cursor.execute("SELECT * FROM proposals WHERE human_status = ? ORDER BY id DESC", (status_filter,))
    else:
        cursor.execute("SELECT * FROM proposals ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        d = dict(r)
        try:
            d["itemized_costs"] = json.loads(d["itemized_costs_json"])
        except Exception:
            d["itemized_costs"] = []
        result.append(d)
    return {"proposals": result}

@router.get("/{quote_number}")
def get_proposal(quote_number: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM proposals WHERE quote_number = ?", (quote_number,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    d = dict(row)
    try:
        d["itemized_costs"] = json.loads(d["itemized_costs_json"])
    except Exception:
        d["itemized_costs"] = []
    return {"proposal": d}

@router.post("/{quote_number}/approve")
def approve_proposal(quote_number: str, payload: ApprovePayload, request: Request):
    # Strictly requires Human Staff or Admin
    user = require_staff_or_admin(request)

    valid_decisions = ["approved", "rejected"]
    if payload.decision not in valid_decisions:
        raise HTTPException(status_code=400, detail="Decision must be 'approved' or 'rejected'")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM proposals WHERE quote_number = ?", (quote_number,))
    prop = cursor.fetchone()
    if not prop:
        conn.close()
        raise HTTPException(status_code=404, detail="Quotation not found")

    now = datetime.now(timezone.utc).isoformat()
    approver_name = f"{user['full_name']} ({user['role'].title()})"

    cursor.execute("""
    UPDATE proposals 
    SET human_status = ?, approved_by = ?, approved_at = ?, approval_notes = ?
    WHERE quote_number = ?
    """, (payload.decision, approver_name, now, payload.approval_notes, quote_number))
    
    # Also update associated lead if exists
    cursor.execute("""
    UPDATE leads 
    SET status = ?
    WHERE email = ?
    """, ("proposal_ready" if payload.decision == "approved" else "in_review", prop["client_email"]))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Quotation {quote_number} has been successfully {payload.decision} by {approver_name}.",
        "quote_number": quote_number,
        "status": payload.decision,
        "approved_by": approver_name,
        "approved_at": now
    }

@router.post("/{quote_number}/send")
def send_proposal(quote_number: str, request: Request):
    require_staff_or_admin(request)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT human_status FROM proposals WHERE quote_number = ?", (quote_number,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    if row["human_status"] != "approved":
        conn.close()
        raise HTTPException(status_code=400, detail="Cannot send proposal to client until it has received executive human approval!")

    cursor.execute("UPDATE proposals SET human_status = 'sent_to_client' WHERE quote_number = ?", (quote_number,))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"Proposal {quote_number} dispatched to client."}

@router.post("/{quote_number}/sign")
def sign_proposal(quote_number: str, request: Request):
    # Customer or Admin signs proposal
    user = get_current_user_from_request(request)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM proposals WHERE quote_number = ?", (quote_number,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Quotation not found")

    signer = user["full_name"] if user else row["client_name"]
    cursor.execute("UPDATE proposals SET human_status = 'signed' WHERE quote_number = ?", (quote_number,))
    
    # Update lead status to won
    cursor.execute("UPDATE leads SET status = 'won' WHERE email = ?", (row["client_email"],))
    conn.commit()
    conn.close()

    return {"success": True, "message": f"Proposal {quote_number} signed and confirmed by {signer}!"}

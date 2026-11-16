from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.database import get_db
from app.auth import require_staff_or_admin, require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])

class SettingUpdatePayload(BaseModel):
    key: str
    value: str

@router.get("/metrics")
def get_metrics(request: Request):
    require_staff_or_admin(request)
    conn = get_db()
    cursor = conn.cursor()

    # Total leads
    cursor.execute("SELECT COUNT(*), SUM(CASE WHEN score='hot' THEN 1 ELSE 0 END) FROM leads")
    row_leads = cursor.fetchone()
    total_leads = row_leads[0] or 0
    hot_leads = row_leads[1] or 0

    # Proposals
    cursor.execute("""
    SELECT COUNT(*), 
           SUM(CASE WHEN human_status='pending_approval' THEN 1 ELSE 0 END),
           SUM(CASE WHEN human_status='approved' THEN 1 ELSE 0 END),
           SUM(total_amount),
           SUM(CASE WHEN human_status='approved' THEN total_amount ELSE 0 END)
    FROM proposals
    """)
    row_p = cursor.fetchone()
    total_proposals = row_p[0] or 0
    pending_approval = row_p[1] or 0
    approved_proposals = row_p[2] or 0
    total_pipeline_val = row_p[3] or 0.0
    approved_revenue = row_p[4] or 0.0

    # Tickets
    cursor.execute("SELECT COUNT(*), SUM(CASE WHEN status='in_repair' OR status='diagnostic_pending' THEN 1 ELSE 0 END) FROM repair_tickets")
    row_t = cursor.fetchone()
    total_tickets = row_t[0] or 0
    active_repairs = row_t[1] or 0

    # E-Waste
    cursor.execute("SELECT COUNT(*), SUM(carbon_offset_kg) FROM ewaste_submissions")
    row_e = cursor.fetchone()
    total_ewaste = row_e[0] or 0
    total_carbon_offset = row_e[1] or 0.0

    # Interaction sessions
    cursor.execute("SELECT COUNT(*) FROM ted_interactions")
    interactions_count = cursor.fetchone()[0] or 0

    # Recent pending approval proposals
    cursor.execute("""
    SELECT id, quote_number, client_name, client_company, project_title, vertical, total_amount, estimated_days, human_status, created_at
    FROM proposals 
    WHERE human_status = 'pending_approval'
    ORDER BY id DESC
    """)
    pending_proposals = [dict(r) for r in cursor.fetchall()]

    # Recent hot leads
    cursor.execute("""
    SELECT id, name, email, company, vertical_interest, estimated_budget, score, status, created_at
    FROM leads
    ORDER BY id DESC
    LIMIT 10
    """)
    recent_leads = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "metrics": {
            "total_leads": total_leads,
            "hot_leads": hot_leads,
            "total_proposals": total_proposals,
            "pending_approval": pending_approval,
            "approved_proposals": approved_proposals,
            "total_pipeline_val": total_pipeline_val,
            "approved_revenue": approved_revenue,
            "total_tickets": total_tickets,
            "active_repairs": active_repairs,
            "total_ewaste": total_ewaste,
            "total_carbon_offset": total_carbon_offset,
            "interactions_count": interactions_count
        },
        "pending_proposals": pending_proposals,
        "recent_leads": recent_leads
    }

@router.get("/campaigns")
def list_campaigns(request: Request):
    require_staff_or_admin(request)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM marketing_campaigns ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return {"campaigns": [dict(r) for r in rows]}

@router.get("/settings")
def get_settings(request: Request):
    require_admin(request)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value, description FROM system_settings")
    rows = cursor.fetchall()
    conn.close()
    return {"settings": {r["key"]: {"value": r["value"], "description": r["description"]} for r in rows}}

@router.post("/settings")
def update_setting(payload: SettingUpdatePayload, request: Request):
    require_admin(request)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE system_settings SET value = ? WHERE key = ?", (payload.value, payload.key))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"Setting '{payload.key}' updated successfully."}

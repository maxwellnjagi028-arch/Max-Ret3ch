from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
from app.database import get_db
from app.auth import require_staff_or_admin

router = APIRouter(prefix="/api", tags=["services"])

class HardwareCreatePayload(BaseModel):
    name: str
    category: str # workstation, gaming_pc, server, laptop, component
    condition: str # new, refurbished_grade_a, certified_renewed
    price: float
    original_price: float
    stock: int = 5
    warranty_months: int = 12
    specs: Dict[str, str]
    image_url: str = "/static/img/titan_workstation.png"
    description: str

@router.get("/services")
def list_services():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM services ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    services = []
    for r in rows:
        d = dict(r)
        try:
            d["features"] = json.loads(d["features_json"])
        except Exception:
            d["features"] = []
        services.append(d)
    return {"services": services}

@router.get("/hardware")
def list_hardware(category: Optional[str] = None, condition: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM hardware_products WHERE 1=1"
    params = []
    if category:
        query += " AND category = ?"
        params.append(category)
    if condition:
        query += " AND condition = ?"
        params.append(condition)
    query += " ORDER BY price DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    items = []
    for r in rows:
        d = dict(r)
        try:
            d["specs"] = json.loads(d["specs_json"])
        except Exception:
            d["specs"] = {}
        items.append(d)
    return {"hardware": items}

@router.post("/hardware")
def add_hardware(payload: HardwareCreatePayload, request: Request):
    require_staff_or_admin(request)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO hardware_products (name, category, condition, price, original_price, stock, warranty_months, specs_json, image_url, description)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payload.name, payload.category, payload.condition, payload.price, payload.original_price,
        payload.stock, payload.warranty_months, json.dumps(payload.specs), payload.image_url, payload.description
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"success": True, "id": new_id, "message": "Hardware product added to inventory."}

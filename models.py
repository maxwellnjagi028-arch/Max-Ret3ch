from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class UserLogin(BaseModel):
    email_or_username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None
    company: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    full_name: str
    phone: Optional[str]
    company: Optional[str]
    created_at: str

# Ted Chat Schemas
class ChatMessage(BaseModel):
    sender: str # "user" or "ted"
    text: str
    timestamp: Optional[str] = None

class TedChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    visitor_name: Optional[str] = None
    visitor_email: Optional[str] = None
    conversation_history: Optional[List[ChatMessage]] = []
    context_hint: Optional[str] = None # e.g. "hardware_diagnostic", "request_proposal", "green_tech"

class TedChatResponse(BaseModel):
    reply: str
    session_id: str
    detected_intent: str
    suggested_actions: List[Dict[str, str]] = []
    generated_proposal: Optional[Dict[str, Any]] = None
    diagnostic_result: Optional[Dict[str, Any]] = None
    lead_captured: bool = False
    requires_human_approval: bool = False
    sentiment: str = "neutral"

# Lead Schemas
class LeadCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    vertical_interest: str
    requirements_summary: str
    estimated_budget: Optional[float] = None
    timeline: Optional[str] = None
    score: Optional[str] = "warm" # hot, warm, cold
    captured_by: Optional[str] = "web_form"
    notes: Optional[str] = None

class LeadStatusUpdate(BaseModel):
    status: str
    score: Optional[str] = None
    notes: Optional[str] = None

# Proposal Schemas
class CostItem(BaseModel):
    item: str
    qty: int = 1
    rate: float
    total: float

class ProposalCreate(BaseModel):
    client_name: str
    client_email: str
    client_company: Optional[str] = None
    project_title: str
    vertical: str
    scope_details: str
    itemized_costs: List[CostItem]
    subtotal: float
    discount: float = 0.0
    tax: float = 0.0
    total_amount: float
    estimated_days: int
    ted_summary: str

class ProposalApproveRequest(BaseModel):
    decision: str # "approved" or "rejected"
    approval_notes: Optional[str] = None

# Repair Ticket Schemas
class RepairTicketCreate(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    device_model: str
    issue_type: str
    symptoms: str
    priority: Optional[str] = "normal"
    diagnosis_by_ted: Optional[str] = None
    estimated_cost: Optional[float] = None

class RepairTicketUpdate(BaseModel):
    status: str
    technician_notes: Optional[str] = None
    estimated_cost: Optional[float] = None
    human_approved_dispatch: Optional[int] = None

# E-Waste Schemas
class EWasteCalculateRequest(BaseModel):
    device_type: str
    quantity: int = 1
    condition: str # working, damaged, dead_motherboard, scrap

class EWasteSubmitRequest(BaseModel):
    client_name: str
    client_email: str
    client_phone: Optional[str] = None
    device_type: str
    quantity: int = 1
    device_condition: str
    calculated_tradein_value: float
    carbon_offset_kg: float
    recycling_type: str = "refurbish_reuse"

# Marketing Campaign Schemas
class CampaignCreate(BaseModel):
    title: str
    target_audience: str
    channel: str # email, linkedin, x_twitter, blog_post, press_release
    goal: Optional[str] = None
    custom_prompt: Optional[str] = None

# System Settings Update
class SettingUpdate(BaseModel):
    key: str
    value: str

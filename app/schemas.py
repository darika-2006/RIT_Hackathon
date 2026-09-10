from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TurnRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier UUID")
    customer_id: str = Field(..., description="Customer ID UUID")
    text: str = Field(..., description="User input text in Tamil or English/Tanglish")
    language: str = Field(default="ta", description="Language code: 'ta' or 'en'")


class ConflictAlert(BaseModel):
    type: str = Field(..., description="Conflict type, e.g. name_mismatch, dob_mismatch, address_mismatch")
    message_ta: str = Field(..., description="Alert message in Tamil")
    message_en: Optional[str] = Field(None, description="Alert message in English")
    severity: str = Field(default="high", description="Severity: low, medium, high")


class UIComponents(BaseModel):
    conflicts: List[ConflictAlert] = Field(default_factory=list)
    action_card: Optional[str] = Field(None, description="Action card identifier for frontend rendering")
    data: Dict[str, Any] = Field(default_factory=dict, description="Card payload data")


class TurnResponse(BaseModel):
    session_id: str
    customer_id: str
    intent: str
    confidence: float
    dialog_state: str
    response_text: str
    language: str = "ta"
    slots: Dict[str, Any] = Field(default_factory=dict)
    ui: UIComponents = Field(default_factory=UIComponents)
    audit_status: str = "logged"


class SessionState(BaseModel):
    session_id: str
    customer_id: str
    dialog_state: str = "GREETING"
    current_intent: Optional[str] = None
    slots: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, str]] = Field(default_factory=list)
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AuditLogPayload(BaseModel):
    customer_id: str
    session_id: str
    agent_name: str = "voice_brain"
    intent: str
    tool_called: str
    result_summary: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Customer360(BaseModel):
    customer_id: str
    full_name: str = Field(..., description="Name as per Aadhaar/Bank records")
    pan_name: Optional[str] = Field(None, description="Name as per PAN card")
    dob: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    account_number: Optional[str] = None
    credit_score: Optional[int] = 720
    is_shg_member: bool = False
    is_kcc_holder: bool = False
    raw_data: Dict[str, Any] = Field(default_factory=dict)

from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

class ORM(BaseModel): model_config = ConfigDict(from_attributes=True)
class SessionCreate(BaseModel): language: Literal["en", "hi"] = "en"
class ChatIn(BaseModel): content: str = Field(min_length=1, max_length=4000)
class MessageOut(ORM): id: str; role: str; content: str; created_at: datetime
class SessionOut(ORM): id: str; language: str; status: str; extracted: dict; summary: dict | None; started_at: datetime; ended_at: datetime | None; messages: list[MessageOut] = []
class ChatOut(BaseModel): session_id: str; response: str; sources: list[dict] = []; tool_events: list[dict] = []
class LeadIn(BaseModel):
    name: str | None = None; email: str | None = None; phone: str | None = None; company: str | None = None
    company_size: int | None = Field(default=None, ge=1); product_interest: str | None = None; requirements: str | None = None
    budget: str | None = None; timeline: str | None = None; authority: str | None = None; objections: str | None = None
    purchase_intent: str | None = None; status: str = "New"; conversation_id: str | None = None
class LeadOut(ORM):
    id: str; name: str | None; email: str | None; phone: str | None; company: str | None; company_size: int | None
    product_interest: str | None; requirements: str | None; budget: str | None; timeline: str | None; authority: str | None
    objections: str | None; purchase_intent: str | None; status: str; score: int; classification: str; score_breakdown: dict; sentiment: str
class BookingIn(BaseModel): lead_id: str; starts_at: datetime; confirmed: bool; idempotency_key: str | None = None
class AppointmentOut(ORM): id: str; lead_id: str; starts_at: datetime; ends_at: datetime; status: str
class SettingsIn(BaseModel):
    agent_name: str = "Aarav"; business_name: str = "NovaCRM"; default_language: Literal["en", "hi"] = "en"
    timezone: str = "Asia/Kolkata"; business_start: int = Field(9, ge=0, le=23); business_end: int = Field(18, ge=1, le=24)
    appointment_minutes: int = Field(30, ge=15, le=120); voice_name: str = ""

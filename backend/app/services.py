import csv, io, re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from . import models

def bant(data: dict) -> tuple[int, str, dict]:
    def points(key):
        value = str(data.get(key) or "").strip()
        known = value.casefold() not in {"", "unknown", "n/a", "none", "not provided", "undecided", "tbd"}
        return {"points": 25 if known else 0, "evidence": value if known else "Unknown"}
    out = {"budget": points("budget"), "authority": points("authority"), "need": points("requirements"), "timeline": points("timeline")}
    score = sum(x["points"] for x in out.values())
    return score, "Hot" if score >= 75 else "Warm" if score >= 40 else "Cold", out

POSITIVE = {"great", "good", "excellent", "interested", "love", "yes", "धन्यवाद", "अच्छा"}
NEGATIVE = {"bad", "expensive", "unhappy", "no", "problem", "hate", "महंगा", "समस्या"}
def sentiment(text: str) -> str:
    words = set(re.findall(r"[\w\u0900-\u097f]+", text.lower()))
    p, n = len(words & POSITIVE), len(words & NEGATIVE)
    return "Positive" if p > n else "Negative" if n > p else "Neutral"

def retrieve(db: Session, query: str, top_k=4):
    rows = db.execute(select(models.Chunk, models.Document).join(models.Document)).all()
    if not rows: return []
    texts = [r.Chunk.text for r in rows]
    try:
        matrix = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5)).fit_transform(texts + [query])
        scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()
    except ValueError: return []
    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [{"document_id": rows[i].Document.id, "filename": rows[i].Document.filename, "chunk": texts[i], "score": round(float(scores[i]), 4)} for i in ranked if scores[i] > 0]

def create_lead(db: Session, data: dict):
    if data.get("email"): data["email"] = data["email"].strip().lower()
    if data.get("phone"): data["phone"] = re.sub(r"\D", "", data["phone"])
    existing = None
    if data.get("email") or data.get("phone"):
        clauses = [models.Lead.email == data["email"]] if data.get("email") else []
        if data.get("phone"): clauses.append(models.Lead.phone == data["phone"])
        existing = db.scalar(select(models.Lead).where(or_(*clauses)))
    lead = existing or models.Lead()
    for k, v in data.items():
        if v is not None and hasattr(lead, k): setattr(lead, k, v)
    score, classification, breakdown = bant({c.name: getattr(lead, c.name) for c in models.Lead.__table__.columns})
    lead.score, lead.classification, lead.score_breakdown = score, classification, breakdown
    if not existing: db.add(lead)
    db.commit(); db.refresh(lead); return lead

def business_settings(db):
    row = db.get(models.Setting, "business")
    return row.value if row else {"agent_name":"Aarav","business_name":"NovaCRM","default_language":"en","timezone":"Asia/Kolkata","business_start":9,"business_end":18,"appointment_minutes":30,"voice_name":""}

def slots(db, day: datetime):
    cfg = business_settings(db); tz = ZoneInfo(cfg["timezone"]); local = day.astimezone(tz)
    start = local.replace(hour=cfg["business_start"], minute=0, second=0, microsecond=0)
    end = local.replace(hour=cfg["business_end"] % 24, minute=0, second=0, microsecond=0)
    if cfg["business_end"] == 24: end = (local + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    occupied = db.execute(select(models.Appointment.starts_at, models.Appointment.ends_at).where(models.Appointment.status == "confirmed")).all()
    result=[]; cursor=start
    while cursor + timedelta(minutes=cfg["appointment_minutes"]) <= end:
        utc=cursor.astimezone(timezone.utc)
        slot_end = (cursor + timedelta(minutes=cfg["appointment_minutes"])).astimezone(timezone.utc)
        if utc > datetime.now(timezone.utc) and not any(
            existing_start.replace(tzinfo=timezone.utc) < slot_end and existing_end.replace(tzinfo=timezone.utc) > utc
            for existing_start, existing_end in occupied
        ):
            result.append(utc)
        cursor += timedelta(minutes=cfg["appointment_minutes"])
    return result

def book(db, lead_id, starts_at, confirmed, key=None):
    if not confirmed: raise ValueError("Explicit customer confirmation is required")
    if not db.get(models.Lead, lead_id): raise ValueError("Invalid lead")
    if starts_at.tzinfo is None: starts_at = starts_at.replace(tzinfo=timezone.utc)
    starts_at = starts_at.astimezone(timezone.utc)
    if starts_at <= datetime.now(timezone.utc): raise ValueError("Past appointments are not allowed")
    cfg=business_settings(db); local=starts_at.astimezone(ZoneInfo(cfg["timezone"]))
    if not cfg["business_start"] <= local.hour < cfg["business_end"]: raise ValueError("Outside business hours")
    if key:
        found=db.scalar(select(models.Appointment).where(models.Appointment.idempotency_key==key))
        if found:
            if found.lead_id != lead_id or found.starts_at.replace(tzinfo=timezone.utc) != starts_at:
                raise ValueError("Booking key belongs to another appointment")
            return found
    if starts_at not in slots(db, starts_at):
        raise ValueError("Time is not an available business slot")
    ap=models.Appointment(lead_id=lead_id, starts_at=starts_at, ends_at=starts_at+timedelta(minutes=cfg["appointment_minutes"]), idempotency_key=key)
    db.add(ap)
    try: db.commit()
    except IntegrityError: db.rollback(); raise ValueError("Time slot is already booked")
    db.refresh(ap); return ap

def analytics(db):
    conv=db.scalar(select(func.count()).select_from(models.Conversation)) or 0
    complete=db.scalar(select(func.count()).select_from(models.Conversation).where(models.Conversation.status=="ended")) or 0
    leads=db.scalar(select(func.count()).select_from(models.Lead)) or 0
    classes=dict(db.execute(select(models.Lead.classification,func.count()).group_by(models.Lead.classification)).all())
    sentiments=dict(db.execute(select(models.Lead.sentiment,func.count()).group_by(models.Lead.sentiment)).all())
    confirmed=db.scalar(select(func.count()).select_from(models.Appointment).where(models.Appointment.status=="confirmed")) or 0
    cancelled=db.scalar(select(func.count()).select_from(models.Appointment).where(models.Appointment.status=="cancelled")) or 0
    durations=[(c.ended_at-c.started_at).total_seconds() for c in db.scalars(select(models.Conversation).where(models.Conversation.ended_at.is_not(None))).all()]
    return {"total_conversations":conv,"completed_conversations":complete,"total_leads":leads,"qualified_leads":classes.get("Hot",0)+classes.get("Warm",0),"lead_distribution":{"Hot":classes.get("Hot",0),"Warm":classes.get("Warm",0),"Cold":classes.get("Cold",0)},"sentiment_distribution":sentiments,"confirmed_appointments":confirmed,"cancelled_appointments":cancelled,"appointment_booking_rate":round(confirmed/conv*100,1) if conv else 0,"average_conversation_duration_seconds":round(sum(durations)/len(durations),1) if durations else 0}

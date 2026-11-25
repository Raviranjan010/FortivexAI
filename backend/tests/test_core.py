from datetime import datetime,timedelta,timezone
from app import models,services
from app import tools
from app import ai


def test_partial_lead_edit_preserves_score_and_normalizes_contact(client):
    lead = client.post("/api/leads", json={"budget": "Approved", "authority": "Unknown"}).json()
    edited = client.put(f"/api/leads/{lead['id']}", json={"email": " SALES@EXAMPLE.TEST "}).json()
    assert edited["email"] == "sales@example.test"
    assert edited["score"] == 25


def test_invalid_settings_and_empty_document_are_rejected(client):
    assert client.put("/api/settings", json={"timezone": "Invalid/Timezone"}).status_code == 422
    assert client.put("/api/settings", json={"business_start": 18, "business_end": 9}).status_code == 422
    assert client.post("/api/documents", files={"file": ("empty.txt", b" ")}).status_code == 422


def test_changed_slot_length_does_not_allow_overlap(client):
    lead = client.post("/api/leads", json={"email": "overlap@example.test"}).json()
    start = (datetime.now(timezone.utc) + timedelta(days=2)).replace(hour=5, minute=0, second=0, microsecond=0)
    payload = {"lead_id": lead["id"], "confirmed": True, "starts_at": start.isoformat()}
    assert client.post("/api/appointments", json=payload).status_code == 200
    assert client.put("/api/settings", json={"appointment_minutes": 15}).status_code == 200
    payload["starts_at"] = (start + timedelta(minutes=15)).isoformat()
    assert client.post("/api/appointments", json=payload).status_code == 409


def test_conversation_to_crm_proposal_booking_and_summary(client, monkeypatch):
    slot = (datetime.now(timezone.utc) + timedelta(days=2)).replace(hour=5, minute=0, second=0, microsecond=0)

    class TestProvider:
        def respond(self, messages, context, language):
            if messages[-1]["role"] == "system":
                return ai.AIResult(response="See the recorded action.")
            assert any(source["filename"] == "pricing.txt" for source in context)
            return ai.AIResult(response="Checking", tool_calls=[
                ai.ToolCall(name="save_lead_to_crm", arguments={
                    "email": "demo@example.test", "budget": "approved", "timeline": "30 days",
                    "authority": "owner", "requirements": "analytics",
                }),
            ]) if messages[-1]["content"] == "Analytics pricing" else ai.AIResult(
                response="Preparing proposal", tool_calls=[
                    ai.ToolCall(name="propose_appointment", arguments={"lead_id": lead_id, "starts_at": slot.isoformat()}),
                    ai.ToolCall(name="confirm_appointment", arguments={"lead_id": lead_id, "starts_at": slot.isoformat(), "confirmed": True}),
                ])

    monkeypatch.setattr(ai, "get_provider", TestProvider)
    client.post("/api/documents", files={"file": ("pricing.txt", b"Analytics pricing for fictional NovaCRM")})
    sid = client.post("/api/conversations", json={}).json()["id"]
    path = f"/api/conversations/{sid}"
    saved = client.post(f"{path}/messages", json={"content": "Analytics pricing"}).json()
    lead_id = saved["tool_events"][0]["result"]["lead_id"]
    reply = client.post(f"{path}/messages", json={"content": "Analytics demo"}).json()
    proposal, rejected = reply["tool_events"]
    assert rejected["status"] == "failed"
    assert client.get("/api/appointments").json() == []
    other = client.post("/api/conversations", json={}).json()["id"]
    assert client.post(f"/api/conversations/{other}/proposals/{proposal['id']}/confirm").status_code == 404
    confirm_url = f"{path}/proposals/{proposal['id']}/confirm"
    booking = client.post(confirm_url).json()
    assert booking["status"] == "confirmed"
    assert client.post(confirm_url).json()["id"] == booking["id"]
    summary = client.post(f"{path}/end").json()["summary"]
    assert summary["appointment_status"] == "confirmed"
    assert summary["lead_score"] == 100
    assert client.get("/api/analytics").json()["confirmed_appointments"] == 1

def test_health_and_no_secret(client):
    assert client.get("/api/health").status_code==200
    body=client.get("/api/config/status").json(); assert "gemini_api_key" not in body
def test_sessions_are_isolated(client,db):
    a=client.post("/api/conversations",json={"language":"en"}).json(); b=client.post("/api/conversations",json={"language":"hi"}).json()
    db.add(models.Message(conversation_id=a["id"],role="user",content="private")); db.commit()
    assert len(client.get(f'/api/conversations/{a["id"]}').json()["messages"])==1
    assert client.get(f'/api/conversations/{b["id"]}').json()["messages"]==[]
def test_bant_unknown_and_full():
    assert services.bant({})[:2]==(0,"Cold")
    score,label,parts=services.bant({"budget":"approved","authority":"decision maker","requirements":"automation","timeline":"30 days"})
    assert score==100 and label=="Hot" and all(x["points"]==25 for x in parts.values())
def test_lead_deduplication(client):
    one=client.post("/api/leads",json={"email":"USER@example.com","budget":"approved"}).json()
    two=client.post("/api/leads",json={"email":"user@example.com","company":"Acme"}).json()
    assert one["id"]==two["id"] and two["company"]=="Acme"
def test_document_lifecycle_and_retrieval(client,db):
    response=client.post("/api/documents",files={"file":("policy.txt",b"Refunds are unavailable after payment. Growth has analytics.","text/plain")})
    assert response.status_code==200
    found=client.get("/api/retrieval",params={"q":"refund policy"}).json()["results"]
    assert found and found[0]["filename"]=="policy.txt"
    did=response.json()["id"]; assert client.delete(f"/api/documents/{did}").status_code==204
    assert not db.query(models.Chunk).filter_by(document_id=did).count()
def test_upload_validation(client):
    assert client.post("/api/documents",files={"file":("x.exe",b"x")}).status_code==415
def test_booking_requires_confirmation_and_prevents_conflict(client):
    lead=client.post("/api/leads",json={"email":"book@example.com"}).json()
    tomorrow=(datetime.now(timezone.utc)+timedelta(days=2)).replace(hour=5,minute=0,second=0,microsecond=0).isoformat()
    payload={"lead_id":lead["id"],"starts_at":tomorrow,"confirmed":False}
    assert client.post("/api/appointments",json=payload).status_code==409
    payload["confirmed"]=True; assert client.post("/api/appointments",json=payload).status_code==200
    assert client.post("/api/appointments",json=payload).status_code==409
def test_past_booking_rejected(client):
    lead=client.post("/api/leads",json={"email":"past@example.com"}).json()
    old=(datetime.now(timezone.utc)-timedelta(days=1)).isoformat()
    assert client.post("/api/appointments",json={"lead_id":lead["id"],"starts_at":old,"confirmed":True}).status_code==409
def test_analytics_real_and_empty(client):
    empty=client.get("/api/analytics").json(); assert empty["total_leads"]==0 and empty["appointment_booking_rate"]==0
    client.post("/api/leads",json={"email":"metric@example.com","requirements":"CRM","timeline":"now"})
    assert client.get("/api/analytics").json()["total_leads"]==1
def test_summary_persists(client):
    session=client.post("/api/conversations",json={}).json()
    end=client.post(f'/api/conversations/{session["id"]}/end').json()
    assert end["status"]=="ended" and end["summary"]["appointment_status"]=="not booked"
def test_tool_registry_validation_and_unknown(db):
    session=models.Conversation(); db.add(session); db.commit()
    result,event=tools.execute(db,session.id,"qualify_lead",{"requirements":"automation","timeline":"30 days"})
    assert result["score"]==50 and event.status=="success"
    result,event=tools.execute(db,session.id,"analyze_sentiment",{"text":"This is great"})
    assert result["sentiment"]=="Positive"
    import pytest
    with pytest.raises(ValueError,match="Unknown tool"): tools.execute(db,session.id,"run_code",{})

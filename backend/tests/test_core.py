from datetime import datetime,timedelta,timezone
from app import models,services
from app import tools

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

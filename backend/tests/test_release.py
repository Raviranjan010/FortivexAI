from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Barrier
from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import ai, models, services
from app import embeddings
from app.appointment_schema import initialize_appointment_schema
from app.database import Base


def test_agent_uses_followup_tools_and_deduplicates(client, monkeypatch):
    calls = [
        [ai.ToolCall(name="update_customer_profile", arguments={"company":"Example CRM"})],
        [ai.ToolCall(name="update_customer_profile", arguments={"company":"Example CRM"}),
         ai.ToolCall(name="qualify_lead", arguments={"budget":"approved"})],
        [],
    ]

    class Provider:
        def respond(self, messages, context, language):
            if len(calls) < 3:
                assert messages[-1]["content"].startswith("Observable tool results:")
            return ai.AIResult(response="Evidence reviewed", tool_calls=calls.pop(0), sentiment="Neutral")

    monkeypatch.setattr(ai, "get_provider", Provider)
    sid = client.post("/api/conversations", json={}).json()["id"]
    path = f"/api/conversations/{sid}"
    response = client.post(path + "/messages", json={"content":"We have an approved CRM budget."})
    assert response.status_code == 200
    assert [event["status"] for event in response.json()["tool_events"]] == ["success", "skipped", "success"]
    assert client.get(path).json()["extracted"]["company"] == "Example CRM"


def test_bant_prioritizes_negative_and_uncertain_evidence():
    score, _, details = services.bant({
        "budget": "Not approved, previously approved",
        "authority": "Not the decision-maker",
        "requirements": "No relevant need",
        "timeline": "Within two weeks",
    })
    assert score == 37
    assert details["budget"]["qualification"] == "Unqualified"
    assert details["authority"]["qualification"] == "Partially qualified"
    assert services.sentiment("This is not good") == "Negative"


def test_semantic_retrieval_caches_chunks_and_filters_weak_matches(db, monkeypatch):
    document = models.Document(filename="plans.txt")
    document.chunks = [models.Chunk(ordinal=0, text="Growth plan costs INR 2999"),
                       models.Chunk(ordinal=1, text="We offer support")]
    db.add(document)
    db.commit()
    calls = []

    def embed(client, model, contents, task):
        calls.append(task)
        return [[1, 0], [0, 1]] if task == "RETRIEVAL_DOCUMENT" else [[1, 0]]

    monkeypatch.setattr(embeddings, "_embed", embed)
    monkeypatch.setattr(embeddings.genai, "Client", lambda **kwargs: object())
    monkeypatch.setattr(embeddings, "get_settings", lambda: SimpleNamespace(
        gemini_embedding_model="test", gemini_api_key="test-double"))
    for query in ("How much would I pay?", "इसकी कीमत क्या है?"):
        result = services.retrieve(db, query)
        assert len(result) == 1 and "2999" in result[0]["chunk"]
        assert result[0]["retrieval_mode"] == "gemini_embeddings"
    assert calls == ["RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY", "RETRIEVAL_QUERY"]


def test_cancel_reopens_slot_and_manual_booking_is_not_conversion(client):
    lead = client.post("/api/leads", json={"email": "release@example.test"}).json()
    client.post("/api/conversations", json={})
    start = (datetime.now(timezone.utc) + timedelta(days=2)).replace(hour=5, minute=0, second=0, microsecond=0)
    payload = {"lead_id": lead["id"], "starts_at": start.isoformat(), "confirmed": True}
    first = client.post("/api/appointments", json=payload)
    assert first.status_code == 200
    assert client.post(f"/api/appointments/{first.json()['id']}/cancel").status_code == 200
    assert client.post("/api/appointments", json=payload).status_code == 200
    assert client.get("/api/analytics").json()["appointment_booking_rate"] == 0


def test_migration_preserves_records_and_serializes_overlapping_writes(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'legacy.db'}")
    with engine.begin() as connection:
        connection.exec_driver_sql("""
            CREATE TABLE appointments (
                id VARCHAR(36) PRIMARY KEY, lead_id VARCHAR(36) NOT NULL,
                starts_at DATETIME NOT NULL, ends_at DATETIME NOT NULL,
                status VARCHAR(20) NOT NULL, idempotency_key VARCHAR(80) UNIQUE, created_at DATETIME NOT NULL,
                CONSTRAINT uq_appointment_start UNIQUE (starts_at))
        """)
        connection.exec_driver_sql("""
            INSERT INTO appointments VALUES
            ('legacy','old','2030-01-01 05:00:00','2030-01-01 05:30:00','cancelled',NULL,'2026-11-26 00:00:00')
        """)
    Base.metadata.create_all(engine)
    initialize_appointment_schema(engine)
    initialize_appointment_schema(engine)
    barrier = Barrier(2)
    start = datetime(2030, 1, 1, 5)

    def insert(offset):
        with Session(engine) as db:
            slot = start + timedelta(minutes=offset)
            db.add(models.Appointment(lead_id="lead", starts_at=slot, ends_at=slot + timedelta(minutes=30)))
            barrier.wait(timeout=5)
            try:
                db.commit()
                return True
            except IntegrityError:
                db.rollback()
                return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(insert, (0, 15))) == [False, True]
    with Session(engine) as db:
        assert db.get(models.Appointment, "legacy").status == "cancelled"

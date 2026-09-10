import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.intent.rules import classify_intent_by_rules
from app.slots.conflict_detector import detect_conflicts
from app.schemas import Customer360

client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["port"] == 8001


@pytest.mark.parametrize(
    "text, expected_intent",
    [
        ("என் கணக்குல எவ்வளவு இருக்கு?", "balance_inquiry"),
        ("balance check pannunga", "balance_inquiry"),
        ("மினி ஸ்டேட்மென்ட் வேணும்", "transaction_history"),
        ("last 5 transactions show me", "transaction_history"),
        ("என் கணக்குல நகை கடன் எவ்வளவு கிடைக்கும்?", "jewel_loan_apply"),
        ("gold loan Apply பண்ணனும்", "jewel_loan_apply"),
        ("முத்ரா கடன் விண்ணப்பம்", "mudra_loan_apply"),
        ("business loan details", "mudra_loan_apply"),
        ("சுய உதவிக் குழு சேமிப்பு இருப்பு", "shg_savings"),
        ("Mathi group savings", "shg_savings"),
        ("பயிர் கடன் குறுவை நிலை", "kcc_status"),
        ("KCC crop loan status", "kcc_status"),
        ("மகளிர் உரிமைத் தொகை வரவு வந்ததா?", "scheme_inquiry"),
        ("PMJDY jan dhan scheme details", "scheme_inquiry"),
        ("உதவி வேண்டும்", "help")
    ]
)
def test_regex_intent_classification(text, expected_intent):
    intent, conf, slots = classify_intent_by_rules(text)
    assert intent == expected_intent
    assert conf >= 0.5


def test_cross_document_conflict_detection():
    # Customer profile with mismatched names
    customer = Customer360(
        customer_id="00000000-0000-0000-0001-000000000001",
        full_name="KAVITHA RAJENDRAN",
        pan_name="KAVITHA R"
    )
    conflicts = detect_conflicts(customer)
    assert len(conflicts) == 1
    c = conflicts[0]
    c_type = c.type if hasattr(c, "type") else c.get("type")
    c_msg = c.message_ta if hasattr(c, "message_ta") else c.get("message_ta")
    c_sev = c.severity if hasattr(c, "severity") else c.get("severity")
    assert c_type == "name_mismatch"
    assert "KAVITHA R" in c_msg
    assert "KAVITHA RAJENDRAN" in c_msg
    assert c_sev == "high"


def test_balance_inquiry_turn():
    payload = {
        "session_id": "test-session-001",
        "customer_id": "00000000-0000-0000-0000-000000000001",
        "text": "என் கணக்குல எவ்வளவு பணம் இருக்கு?",
        "language": "ta"
    }
    response = client.post("/v1/turn", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "balance_inquiry"
    assert ("125,000" in data["response_text"] or "15,430" in data["response_text"])
    assert data["audit_status"] == "logged"


def test_hero_jewel_loan_multiturn_flow():
    session_id = "hero-flow-session-002"
    customer_id = "00000000-0000-0000-0001-000000000001"

    # Turn 1: Trigger jewel loan
    r1 = client.post("/v1/turn", json={
        "session_id": session_id,
        "customer_id": customer_id,
        "text": "எனக்கு நகை கடன் வேணும்",
        "language": "ta"
    })
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["intent"] == "jewel_loan_apply"
    assert d1["dialog_state"] in ("SLOT_FILLING", "GREETING")

    # Turn 2: Provide weight and jewel type
    r2 = client.post("/v1/turn", json={
        "session_id": session_id,
        "customer_id": customer_id,
        "text": "16 கிராம் சங்கிலி",
        "language": "ta"
    })
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["slots"].get("jewel_weight_grams") == 16.0
    assert d2["slots"].get("jewel_type") == "chain"

    # Turn 3: Provide requested loan amount
    r3 = client.post("/v1/turn", json={
        "session_id": session_id,
        "customer_id": customer_id,
        "text": "75000 ரூபாய் கடன் வேணும்",
        "language": "ta"
    })
    assert r3.status_code == 200
    d3 = r3.json()
    assert d3["slots"].get("requested_amount") == 75000.0
    assert d3["dialog_state"] == "CONFIRM"
    assert "உறுதிப்படுத்த" in d3["response_text"] or "confirm" in d3["response_text"].lower()

    # Turn 4: User confirms loan application
    r4 = client.post("/v1/turn", json={
        "session_id": session_id,
        "customer_id": customer_id,
        "text": "சரி",
        "language": "ta"
    })
    assert r4.status_code == 200
    d4 = r4.json()
    assert d4["dialog_state"] == "EXECUTE"
    assert "விண்ணப்ப எண்" in d4["response_text"] or "Reference ID" in d4["response_text"]

import logging
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import (
    TurnRequest,
    TurnResponse,
    AuditLogPayload,
    UIComponents
)
from app.intent.classifier import classify_intent
from app.dialog.session import session_manager
from app.dialog.state_machine import state_machine
from app.slots.conflict_detector import detect_conflicts
from app.integrations.bank_api import bank_api
from app.response.generator import generate_response

# Configure Logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("brain_service")

# Initialize FastAPI App
app = FastAPI(
    title="Tamil Nadu Vernacular Voice Micro-Banking Assistant - Brain Service",
    version="1.0.0",
    description="Tamil-first & Tanglish voice brain service for micro-loans, SHG savings, and crop loans."
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "voice_brain_service",
        "port": settings.PORT,
        "environment": settings.ENVIRONMENT
    }


@app.get("/v1/test-db", tags=["Health & Diagnostics"])
async def test_db_connection():
    """Test endpoint to verify live backend database connection to friend's machine"""
    try:
        profile = await bank_api.get_customer_360(settings.DEFAULT_DEMO_CUSTOMER_ID)
        balance = await bank_api.get_account_balance(settings.DEFAULT_DEMO_CUSTOMER_ID)
        return {
            "status": "connected",
            "backend_url": settings.BANK_API_BASE_URL,
            "demo_customer_profile": profile.model_dump(),
            "account_balance": balance
        }
    except Exception as e:
        return {
            "status": "error",
            "backend_url": settings.BANK_API_BASE_URL,
            "error_detail": str(e)
        }


@app.post("/v1/turn", response_model=TurnResponse, tags=["Voice Brain Turn"])
async def process_turn(request: TurnRequest):
    """
    Core conversational turn engine:
    1. Retrieves Redis session state.
    2. Classifies Tamil/Tanglish intent via Ollama/Groq/Rules.
    3. Fetches Customer 360 profile from Bank API Port 8000.
    4. Performs cross-document conflict detection (PAN vs Aadhaar name match).
    5. Executes slot filling and dialog state machine.
    6. Fetches required financial data from Backend Port 8000.
    7. Generates zero-hallucination response from strict templates.
    8. Async posts audit log to Backend Port 8000.
    9. Persists session state with 30m TTL.
    """
    logger.info(f"Processing turn for session={request.session_id}, customer={request.customer_id}, text='{request.text}'")

    try:
        # 1. Retrieve session state
        session_data = await session_manager.get_session(request.session_id)
        session_data["customer_id"] = request.customer_id

        # 2. Classify intent
        intent, confidence, extracted_slots = await classify_intent(request.text)
        
        # If in SLOT_FILLING or CONFIRM state and new intent is unclear, preserve session's active intent
        if (intent == "unclear" or confidence < 0.5) and session_data.get("current_intent") and session_data.get("dialog_state") in ("SLOT_FILLING", "CONFIRM"):
            intent = session_data["current_intent"]
            logger.info(f"Preserving active session intent '{intent}' during {session_data.get('dialog_state')} state")

        logger.info(f"Intent resolved: {intent} (conf={confidence:.2f}), slots={extracted_slots}")

        # 3. Fetch Customer 360 profile
        customer_profile = await bank_api.get_customer_360(request.customer_id)

        # 4. Conflict detection
        conflicts = detect_conflicts(customer_profile)

        # 5. Process state machine and slot filling
        new_state, updated_slots, next_prompt = state_machine.process_turn(
            intent=intent,
            extracted_slots=extracted_slots,
            current_session_state=session_data,
            user_text=request.text,
            customer_profile=customer_profile
        )

        # 6. Perform Bank API interactions based on intent and state
        bank_data = {}
        tool_called = "none"

        if intent == "balance_inquiry":
            tool_called = "bank_api.get_account_balance"
            bank_data = await bank_api.get_account_balance(request.customer_id)
        elif intent == "transaction_history":
            tool_called = "bank_api.get_transaction_history"
            bank_data = await bank_api.get_transaction_history(request.customer_id, limit=5)
        elif intent == "jewel_loan_apply":
            if new_state == "EXECUTE":
                tool_called = "bank_api.apply_jewel_loan"
                payload = {**updated_slots, "customer_id": request.customer_id}
                bank_data = await bank_api.apply_jewel_loan(payload)
            else:
                tool_called = "slots.engine.process_slots"
        elif intent == "mudra_loan_apply":
            if new_state == "EXECUTE":
                tool_called = "bank_api.apply_mudra_loan"
                payload = {**updated_slots, "customer_id": request.customer_id}
                bank_data = await bank_api.apply_mudra_loan(payload)
            else:
                tool_called = "slots.engine.process_slots"
        elif intent == "shg_savings":
            tool_called = "bank_api.get_shg_details"
            bank_data = await bank_api.get_shg_details(request.customer_id)
        elif intent == "kcc_status":
            tool_called = "bank_api.get_kcc_status"
            bank_data = await bank_api.get_kcc_status(request.customer_id)
        elif intent == "scheme_inquiry":
            tool_called = "bank_api.get_scheme_inquiry"
            bank_data = await bank_api.get_scheme_inquiry(request.customer_id)

        # 7. Generate response text & UI action card
        response_text, ui_components = generate_response(
            intent=intent,
            language=request.language,
            dialog_state=new_state,
            slots=updated_slots,
            bank_data=bank_data,
            conflicts=conflicts,
            next_prompt=next_prompt
        )

        now_utc = datetime.now(timezone.utc).isoformat()

        # 8. Post audit log to Backend Port 8000
        audit_payload = AuditLogPayload(
            customer_id=request.customer_id,
            session_id=request.session_id,
            agent_name="voice_brain",
            intent=intent,
            tool_called=tool_called,
            result_summary=response_text[:120],
            timestamp=now_utc
        )
        await bank_api.post_audit_log(audit_payload)

        # 9. Update & save session state
        session_data["dialog_state"] = new_state
        session_data["current_intent"] = intent
        session_data["slots"] = updated_slots
        session_data["history"].append({
            "timestamp": now_utc,
            "user_text": request.text,
            "bot_text": response_text,
            "intent": intent
        })
        await session_manager.save_session(request.session_id, session_data)

        # 10. Construct turn response
        return TurnResponse(
            session_id=request.session_id,
            customer_id=request.customer_id,
            intent=intent,
            confidence=confidence,
            dialog_state=new_state,
            response_text=response_text,
            language=request.language,
            slots=updated_slots,
            ui=ui_components,
            audit_status="logged"
        )

    except Exception as e:
        logger.error(f"Error processing turn: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Brain Service Error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)

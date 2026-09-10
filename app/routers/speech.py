import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, File, Form, UploadFile, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, Field

from app.speech.asr_client import asr_client, AsrError
from app.speech.tts_client import tts_client
from app.routers.turn import process_turn_logic, TurnInput, TurnOutput, UIState
from app.response.templates import TEMPLATES

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Speech & Voice"])


class TranscribeResponse(BaseModel):
    text: str
    confidence: Optional[float] = 0.92
    language: Optional[str] = "ta"
    raw: Optional[Dict[str, Any]] = Field(default_factory=dict)
    source: str = "http_asr"


class ASRMetadata(BaseModel):
    text: str
    confidence: Optional[float] = 0.92
    language: Optional[str] = "ta"


class VoiceTurnOutput(TurnOutput):
    asr: ASRMetadata
    transcript: str
    tts_audio_base64: Optional[str] = None


@router.post("/v1/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    file: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    language: Optional[str] = Form("ta"),
    session_id: Optional[str] = Form(None)
):
    """
    Audio transcription endpoint.
    Accepts multipart file upload ('file' or 'audio') and returns normalized ASR JSON payload.
    Does NOT invoke banking turn logic.
    """
    target_file = file or audio
    if not target_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing audio file upload. Provide multipart form field 'file' or 'audio'."
        )

    audio_bytes = await target_file.read()

    try:
        res = await asr_client.transcribe(
            audio_bytes=audio_bytes,
            filename=target_file.filename or "audio.webm",
            content_type=target_file.content_type or "audio/webm",
            language_hint=language,
            session_id=session_id
        )
        return TranscribeResponse(
            text=res["text"],
            confidence=res.get("confidence", 0.92),
            language=res.get("language", language or "ta"),
            raw=res.get("raw", {}),
            source=res.get("source", "http_asr")
        )
    except AsrError as ae:
        logger.error(f"ASR transcription failed: {ae}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"ASR Service Error: {ae.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in transcribe_audio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )


@router.post("/v1/voice_turn", response_model=VoiceTurnOutput)
async def voice_turn(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    session_id: str = Form(..., description="Session UUID string"),
    customer_id: str = Form(..., description="Customer UUID string"),
    language: Optional[str] = Form("ta", description="Language hint: 'ta' or 'en'")
):
    """
    Single unified Voice Turn endpoint:
    1. Transcribes incoming audio stream via ASR.
    2. Executes Smart Router turn logic.
    3. Synthesizes response audio via TTS if enabled.
    4. Returns complete TurnResponse combined with ASR metadata and transcript.
    """
    target_file = file or audio
    if not target_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing audio file upload. Provide multipart form field 'file' or 'audio'."
        )

    audio_bytes = await target_file.read()
    lang = language or "ta"

    # 1. Transcribe audio via ASR
    asr_res = None
    try:
        asr_res = await asr_client.transcribe(
            audio_bytes=audio_bytes,
            filename=target_file.filename or "audio.webm",
            content_type=target_file.content_type or "audio/webm",
            language_hint=lang,
            session_id=session_id
        )
    except AsrError as ae:
        logger.error(f"Voice Turn ASR error: {ae}")
        # Graceful degradation: Return Tamil speech error message without crashing
        error_text = "மன்னிக்கவும், உங்கள் குரலை கேட்க முடியவில்லை. ASR சேவை தற்காலிகமாக கிடைக்கவில்லை."
        return VoiceTurnOutput(
            response_text=error_text,
            intent="unclear",
            confidence=0.0,
            dialog_state="ERROR",
            slots={},
            ui=UIState(questions_total=22, questions_remaining=0, conflicts=[]),
            audit_status="error",
            asr=ASRMetadata(text="", confidence=0.0, language=lang),
            transcript="",
            tts_audio_base64=None
        )

    transcribed_text = asr_res.get("text", "").strip()
    asr_meta = ASRMetadata(
        text=transcribed_text,
        confidence=asr_res.get("confidence", 0.92),
        language=asr_res.get("language", lang)
    )

    # 2. Check empty transcript
    if not transcribed_text:
        empty_text = "மன்னிக்கவும், உங்கள் குரல் தெளிவாக கேட்கவில்லை. மீண்டும் கூறவும்."
        return VoiceTurnOutput(
            response_text=empty_text,
            intent="unclear",
            confidence=0.3,
            dialog_state="GREETING",
            slots={},
            ui=UIState(questions_total=22, questions_remaining=0, conflicts=[]),
            audit_status="logged",
            asr=asr_meta,
            transcript="",
            tts_audio_base64=None
        )

    # 3. Pass transcribed text to shared turn orchestrator
    turn_input = TurnInput(
        session_id=session_id,
        customer_id=customer_id,
        text=transcribed_text,
        language=lang
    )
    turn_output: TurnOutput = await process_turn_logic(turn_input, background_tasks)

    # 4. Optional TTS synthesis
    tts_audio = await tts_client.synthesize(turn_output.response_text, language=lang)

    # 5. Return unified VoiceTurnOutput
    return VoiceTurnOutput(
        response_text=turn_output.response_text,
        intent=turn_output.intent,
        confidence=turn_output.confidence,
        dialog_state=turn_output.dialog_state,
        slots=turn_output.slots,
        ui=turn_output.ui,
        audit_status=turn_output.audit_status,
        asr=asr_meta,
        transcript=transcribed_text,
        tts_audio_base64=tts_audio
    )

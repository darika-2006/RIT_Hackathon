import io
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_asr_defaults_point_to_dedicated_asr_server():
    from app.config import settings

    assert settings.ASR_BASE_URL == "http://172.16.149.221:8002"
    assert settings.ASR_ENDPOINT_PATH == "/api/v1/transcribe"


def test_transcribe_endpoint_with_mock_asr():
    """Test 1: POST /v1/transcribe with mock ASR client"""
    mock_res = {
        "text": "என் கணக்கு பாலன்ஸ் எவ்வளவு",
        "confidence": 0.95,
        "language": "ta",
        "raw": {"text": "என் கணக்கு பாலன்ஸ் எவ்வளவு"},
        "source": "http_asr"
    }

    dummy_audio = io.BytesIO(b"RIFF dummy wav audio data header")

    with patch("app.routers.speech.asr_client.transcribe", new_callable=AsyncMock) as mock_transcribe:
        mock_transcribe.return_value = mock_res
        
        response = client.post(
            "/v1/transcribe",
            files={"file": ("sample_ta.wav", dummy_audio, "audio/wav")},
            data={"language": "ta", "session_id": "test-session-asr-1"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "என் கணக்கு பாலன்ஸ் எவ்வளவு"
        assert data["confidence"] == 0.95
        assert data["language"] == "ta"
        assert data["source"] == "http_asr"


def test_voice_turn_calls_process_turn():
    """Test 2: POST /v1/voice_turn calls process_turn with transcribed Tamil text"""
    mock_asr_res = {
        "text": "என் கணக்கு பாலன்ஸ்",
        "confidence": 0.96,
        "language": "ta",
        "raw": {},
        "source": "http_asr"
    }

    dummy_audio = io.BytesIO(b"RIFF dummy wav audio data header")

    with patch("app.routers.speech.asr_client.transcribe", new_callable=AsyncMock) as mock_transcribe:
        mock_transcribe.return_value = mock_asr_res

        response = client.post(
            "/v1/voice_turn",
            files={"file": ("sample_ta.wav", dummy_audio, "audio/wav")},
            data={
                "session_id": "voice-session-001",
                "customer_id": "00000000-0000-0000-0000-000000000001",
                "language": "ta"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "balance_inquiry"
        assert data["transcript"] == "என் கணக்கு பாலன்ஸ்"
        assert data["asr"]["text"] == "என் கணக்கு பாலன்ஸ்"
        assert data["asr"]["confidence"] == 0.96
        assert "இருப்பு" in data["response_text"] or "balance" in data["response_text"].lower()


def test_voice_turn_empty_transcript_returns_error_tamil():
    """Test 3: POST /v1/voice_turn when ASR returns empty text returns Tamil fallback message"""
    mock_asr_res = {
        "text": "",
        "confidence": 0.0,
        "language": "ta",
        "raw": {},
        "source": "http_asr"
    }

    dummy_audio = io.BytesIO(b"RIFF dummy wav audio data header")

    with patch("app.routers.speech.asr_client.transcribe", new_callable=AsyncMock) as mock_transcribe:
        mock_transcribe.return_value = mock_asr_res

        response = client.post(
            "/v1/voice_turn",
            files={"file": ("silent.wav", dummy_audio, "audio/wav")},
            data={
                "session_id": "voice-session-002",
                "customer_id": "00000000-0000-0000-0000-000000000001",
                "language": "ta"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "unclear"
        assert "குரல் தெளிவாக கேட்கவில்லை" in data["response_text"]

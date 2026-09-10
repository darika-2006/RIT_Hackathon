# Tamil Nadu Voice Micro-Banking Assistant - Integration Guide

This guide documents the API endpoints, request contracts, response payloads, and example `curl` commands for both **Text-based** and **Voice-based** conversational turns.

---

## Architecture Overview

```
[Frontend Client (Mic / Web UI)]
        │
        ├── 1. Text Turn Payload ────────────► POST /v1/turn (Port 8001)
        ├── 2. Audio Only (ASR) ─────────────► POST /v1/transcribe (Port 8001)
        └── 3. Direct Voice Turn (Audio) ────► POST /v1/voice_turn (Port 8001)
                                                       │
                                                       ▼
                                           [Smart Router Orchestrator]
                                           (Intent Classifier → Bank API 
                                            → Slot Engine → Response Templates)

Brain Service (Port 8001)
        ├── Remote Qwen LLM ────────────────► 172.16.149.221:8000/v1
        │   (intent classification only)
        └── Dedicated Whisper ASR ──────────► 172.16.149.221:8002/api/v1/transcribe
            (audio transcription only)
```

---

## 1. Text Turn Endpoint (`POST /v1/turn`)

Used when the frontend already has user text (or performs ASR client-side).

- **URL**: `http://localhost:8001/v1/turn`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "session_id": "00000000-0000-0000-0000-000000000001",
  "customer_id": "00000000-0000-0000-0000-000000000001",
  "text": "என் கணக்கு பாலன்ஸ் எவ்வளவு",
  "language": "ta"
}
```

- **Example `curl`**:
```bash
curl -s -X POST http://localhost:8001/v1/turn \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "s1",
    "customer_id": "00000000-0000-0000-0000-000000000001",
    "text": "என் கணக்கு பாலன்ஸ்",
    "language": "ta"
  }'
```

- **Response Payload**:
```json
{
  "response_text": "வணக்கம் Aarav Sharma! உங்கள் கணக்கில் (5011000100010001) இருப்பு ₹125,000.00 உள்ளது.",
  "intent": "balance_inquiry",
  "confidence": 0.95,
  "dialog_state": "EXECUTE",
  "slots": {},
  "ui": {
    "questions_total": 22,
    "questions_remaining": 0,
    "conflicts": [],
    "action_card": "balance_card",
    "data": {
      "account_number": "5011000100010001",
      "balance": 125000.0
    }
  },
  "audit_status": "logged"
}
```

---

## 2. ASR Audio Transcription Only (`POST /v1/transcribe`)

Transcribes audio file to text using the ASR engine (Whisper / Groq / Microservice).

The client calls the Brain Service on port 8001. The Brain Service forwards the
audio to the dedicated ASR server on port 8002; it does not send audio to the
remote Qwen LLM on port 8000.

- **URL**: `http://localhost:8001/v1/transcribe`
- **Headers**: `Content-Type: multipart/form-data`
- **Form Fields**:
  - `file`: Audio file (`.wav`, `.webm`, `.mp3`, `.ogg`)
  - `language`: `ta` (optional, default `ta`)
  - `session_id`: Session UUID string (optional)

- **Example `curl`**:
```bash
curl -s -X POST http://localhost:8001/v1/transcribe \
  -F 'file=@sample_ta.wav' \
  -F 'language=ta'
```

To test the ASR host directly after it is deployed:
```bash
curl --connect-timeout 3 --max-time 45 -sS -X POST \
  http://172.16.149.221:8002/api/v1/transcribe \
  -F 'file=@/absolute/path/sample_ta.wav' \
  -F 'language=ta' \
  -F 'session_id=test-001'
```

### Deploying the dedicated ASR service

Run this on the ASR host, not on the Brain Service host. Set `GROQ_API_KEY` in
that host's secret manager or shell environment, then start the included server:

```bash
export GROQ_API_KEY='replace-with-a-rotated-key'
export ASR_HOST=0.0.0.0
export ASR_PORT=8002
python asr_server.py
```

Allow inbound TCP port 8002 only from the Brain Service host or LAN. The remote
Qwen server remains on port 8000 and is never used for transcription.

- **Response Payload**:
```json
{
  "text": "என் கணக்கு பாலன்ஸ் எவ்வளவு",
  "confidence": 0.95,
  "language": "ta",
  "raw": {},
  "source": "http_asr"
}
```

---

## 3. Direct Unified Voice Turn Endpoint (`POST /v1/voice_turn`)

Transcribes microphone audio, runs intent classification & banking orchestration, and returns turn response with ASR metadata in a single call.

- **URL**: `http://localhost:8001/v1/voice_turn`
- **Headers**: `Content-Type: multipart/form-data`
- **Form Fields**:
  - `file`: Audio file (`.wav`, `.webm`, `.mp3`, `.ogg`)
  - `session_id`: Session UUID string (required)
  - `customer_id`: Customer UUID string (required)
  - `language`: `ta` or `en` (optional, default `ta`)

- **Example `curl`**:
```bash
curl -s -X POST http://localhost:8001/v1/voice_turn \
  -F 'file=@sample_ta.wav' \
  -F 'session_id=s1' \
  -F 'customer_id=00000000-0000-0000-0000-000000000001' \
  -F 'language=ta'
```

- **Response Payload**:
```json
{
  "response_text": "வணக்கம் Aarav Sharma! உங்கள் கணக்கில் (5011000100010001) இருப்பு ₹125,000.00 உள்ளது.",
  "intent": "balance_inquiry",
  "confidence": 0.95,
  "dialog_state": "EXECUTE",
  "slots": {},
  "ui": {
    "questions_total": 22,
    "questions_remaining": 0,
    "conflicts": [],
    "action_card": "balance_card",
    "data": {
      "account_number": "5011000100010001",
      "balance": 125000.0
    }
  },
  "audit_status": "logged",
  "asr": {
    "text": "என் கணக்கு பாலன்ஸ் எவ்வளவு",
    "confidence": 0.95,
    "language": "ta"
  },
  "transcript": "என் கணக்கு பாலன்ஸ் எவ்வளவு",
  "tts_audio_base64": null
}
```

---

## 4. Health & Status Endpoints

- **Brain Service General Health**: `GET http://localhost:8001/health`
- **ASR Engine Health**: `GET http://localhost:8001/health/asr`
- **Database Connection Check**: `GET http://localhost:8001/v1/test-db`

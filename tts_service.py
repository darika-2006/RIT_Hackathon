"""
Micro-Banking Voice Assistant — Text-to-Speech (TTS) Service
Powered by ONNX VITS (ai4bharat/vits_rasa_13: model_int8.onnx) as the primary engine,
with optional Edge-TTS fallback.
"""

import asyncio
import io
import os
import re
import wave
import numpy as np
import edge_tts

MODEL_PATH = os.path.join(os.path.dirname(__file__), "onnx", "model_int8.onnx")
TOKENS_PATH = os.path.join(os.path.dirname(__file__), "onnx", "tokens.txt")

# Load ONNX vocabulary dictionary
token2id = {}
if os.path.exists(TOKENS_PATH):
    with open(TOKENS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                token2id[parts[0]] = int(parts[1])

# Load ONNX VITS runtime session
onnx_session = None
if os.path.exists(MODEL_PATH):
    try:
        import onnxruntime as ort
        onnx_session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
        print(f"[TTS] Loaded ONNX model successfully: {MODEL_PATH}")
    except Exception as e:
        print(f"[TTS WARNING] Could not load ONNX model: {e}")

# ONNX speaker IDs for Indic languages
ONNX_SPEAKER_MAP = {
    "hi": 0,    # Hindi
    "ta": 20,   # Tamil
    "te": 30,   # Telugu
    "kn": 40,   # Kannada
    "ml": 45,   # Malayalam
    "pa": 50,   # Punjabi
    "bn": 60,   # Bengali
    "mr": 70,   # Marathi
    "gu": 80,   # Gujarati
    "ne": 90,   # Nepali
    "sa": 100,  # Sanskrit
    "as": 10,   # Assamese
    "ur": 110,  # Urdu
    "en": 0,    # Default speaker for English
}

# Edge-TTS voice mapping (optional fallback)
EDGE_VOICE_MAP = {
    "hi": "hi-IN-SwaraNeural",
    "ta": "ta-IN-PallaviNeural",
    "te": "te-IN-ShrutiNeural",
    "kn": "kn-IN-SapnaNeural",
    "ml": "ml-IN-SobhanaNeural",
    "bn": "bn-IN-TanishaaNeural",
    "mr": "mr-IN-AarohiNeural",
    "gu": "gu-IN-DhwaniNeural",
    "ur": "ur-IN-GulNeural",
    "ne": "ne-NP-HemkalaNeural",
    "en": "en-IN-NeerjaNeural",
}

def format_financial_text(text: str, lang: str = "hi") -> str:
    """Cleans currency and numbers for natural pronunciation."""
    if lang == "hi":
        text = re.sub(r'₹\s*([0-9,]+)', r'\1 रुपये', text)
        text = re.sub(r'Rs\.?\s*([0-9,]+)', r'\1 रुपये', text)
        text = re.sub(r'(?<=\d),(?=\d)', '', text)
    return text

def run_onnx_synthesis(text: str, speaker_id: int = 0) -> bytes:
    """Executes model_int8.onnx on CPU and returns WAV audio bytes."""
    if onnx_session is None:
        raise RuntimeError("ONNX model is not loaded. Ensure onnx/model_int8.onnx exists.")

    tokens = [token2id[c] for c in text if c in token2id]
    if not tokens:
        raise ValueError(f"No matching characters found in ONNX tokens.txt for text: '{text[:20]}...'")

    # VITS interleave blank token 0
    tokens_with_blank = [0]
    for t in tokens:
        tokens_with_blank.extend([t, 0])

    x = np.array([tokens_with_blank], dtype=np.int64)
    xl = np.array([len(tokens_with_blank)], dtype=np.int64)

    outputs = onnx_session.run(
        ["y"],
        {
            "x": x,
            "x_length": xl,
            "noise_scale": np.array(0.667, dtype=np.float32),
            "length_scale": np.array(1.0, dtype=np.float32),
            "noise_scale_w": np.array(0.8, dtype=np.float32),
            "sid": np.array([speaker_id], dtype=np.int64),
            "emotion_id": np.array([0], dtype=np.int64),
        },
    )

    audio_samples = outputs[0][0, 0]
    audio_int16 = (audio_samples * 32767).clip(-32768, 32767).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(audio_int16.tobytes())

    return buf.getvalue()

async def run_edge_synthesis(text: str, voice: str) -> bytes:
    """Executes Edge-TTS neural synthesis and returns MP3 audio bytes."""
    communicate = edge_tts.Communicate(text, voice)
    audio_stream = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_stream.write(chunk["data"])
    return audio_stream.getvalue()

async def synthesize_speech(text: str, language: str = "hi", engine: str = "onnx") -> tuple[bytes, str]:
    """
    Main TTS entry point for the banking application.
    - engine='onnx' (DEFAULT): runs onnx/model_int8.onnx locally.
    - engine='edge': runs cloud neural Edge-TTS.
    Returns: (audio_bytes, media_type)
    """
    clean_text = format_financial_text(text, language)

    # 1. Primary Engine: ONNX VITS (model_int8.onnx)
    if engine.lower() == "onnx":
        sid = ONNX_SPEAKER_MAP.get(language, 0)
        try:
            wav_bytes = run_onnx_synthesis(clean_text, speaker_id=sid)
            return wav_bytes, "audio/wav"
        except Exception as e:
            print(f"[ONNX TTS Error] {e}. Trying Edge-TTS fallback...")
            # Fallback to Edge if ONNX fails on specific characters
            voice = EDGE_VOICE_MAP.get(language, "hi-IN-SwaraNeural")
            mp3_bytes = await run_edge_synthesis(clean_text, voice)
            return mp3_bytes, "audio/mpeg"

    # 2. Alternative Engine: Edge-TTS
    else:
        voice = EDGE_VOICE_MAP.get(language, "hi-IN-SwaraNeural")
        mp3_bytes = await run_edge_synthesis(clean_text, voice)
        return mp3_bytes, "audio/mpeg"

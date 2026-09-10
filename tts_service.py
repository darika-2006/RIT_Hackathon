"""
Micro-Banking Voice Assistant — Text-to-Speech (TTS) Service
Supports 14 Indian Languages + Indian English using a hybrid architecture:
- High-fidelity Neural voices (edge-tts) for major vernacular languages
- Offline VITS ONNX model (ai4bharat/vits_rasa_13) for Punjabi, Assamese, Sanskrit
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

# Load ONNX resources
token2id = {}
if os.path.exists(TOKENS_PATH):
    with open(TOKENS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                token2id[parts[0]] = int(parts[1])

onnx_session = None
if os.path.exists(MODEL_PATH):
    try:
        import onnxruntime as ort
        onnx_session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
    except Exception as e:
        print(f"[TTS WARNING] Could not load ONNX model: {e}")

VOICE_CONFIG = {
    "hi": ("edge", "hi-IN-SwaraNeural"),
    "ta": ("edge", "ta-IN-PallaviNeural"),
    "te": ("edge", "te-IN-ShrutiNeural"),
    "kn": ("edge", "kn-IN-SapnaNeural"),
    "ml": ("edge", "ml-IN-SobhanaNeural"),
    "bn": ("edge", "bn-IN-TanishaaNeural"),
    "mr": ("edge", "mr-IN-AarohiNeural"),
    "gu": ("edge", "gu-IN-DhwaniNeural"),
    "pa": ("onnx", 50),
    "as": ("onnx", 10),
    "ur": ("edge", "ur-IN-GulNeural"),
    "sa": ("onnx", 100),
    "ne": ("edge", "ne-NP-HemkalaNeural"),
    "en": ("edge", "en-IN-NeerjaNeural"),
}

def format_financial_text(text: str, lang: str = "hi") -> str:
    """Cleans currency and numbers for natural vernacular pronunciation."""
    if lang == "hi":
        text = re.sub(r'₹\s*([0-9,]+)', r'\1 रुपये', text)
        text = re.sub(r'Rs\.?\s*([0-9,]+)', r'\1 रुपये', text)
        text = re.sub(r'(?<=\d),(?=\d)', '', text)
    return text

async def synthesize_speech(text: str, language: str = "hi") -> tuple[bytes, str]:
    """
    Synthesizes speech for the given text and language.
    Returns: (audio_bytes, media_type)
    """
    clean_text = format_financial_text(text, language)
    cfg = VOICE_CONFIG.get(language, ("edge", "hi-IN-SwaraNeural"))
    engine, param = cfg

    if engine == "edge":
        communicate = edge_tts.Communicate(clean_text, param)
        audio_stream = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])
        return audio_stream.getvalue(), "audio/mpeg"

    elif engine == "onnx" and onnx_session is not None:
        tokens = [token2id[c] for c in clean_text if c in token2id]
        if not tokens:
            raise ValueError(f"Characters not recognized for language '{language}' in ONNX vocabulary.")
        tb = [0]
        for t in tokens:
            tb.extend([t, 0])
        x = np.array([tb], dtype=np.int64)
        xl = np.array([len(tb)], dtype=np.int64)
        out = onnx_session.run(
            ["y"],
            {
                "x": x,
                "x_length": xl,
                "noise_scale": np.array(0.667, dtype=np.float32),
                "length_scale": np.array(1.0, dtype=np.float32),
                "noise_scale_w": np.array(0.8, dtype=np.float32),
                "sid": np.array([param], dtype=np.int64),
                "emotion_id": np.array([0], dtype=np.int64),
            },
        )[0]
        audio_samples = (out[0, 0] * 32767).clip(-32768, 32767).astype(np.int16)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(audio_samples.tobytes())
        return buf.getvalue(), "audio/wav"

    else:
        communicate = edge_tts.Communicate(clean_text, "hi-IN-SwaraNeural")
        audio_stream = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])
        return audio_stream.getvalue(), "audio/mpeg"

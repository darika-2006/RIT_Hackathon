# 🏦 Vernacular Voice-First Micro-Banking Assistant — ASR Engine

A high-performance Automatic Speech Recognition (ASR) service tailored for Indian micro-banking applications (Jan Dhan, Mudra loans, KCC, SHG savings). Built with **FastAPI** and powered by **Whisper Large v3 Turbo** on **Groq Cloud** for ultra-low latency transcription across Indian vernacular and code-mixed languages.

---

## 🚀 Key Features

- **Sub-Second Latency:** Powered by Groq Cloud LPU acceleration (~300ms–800ms transcription time).
- **Vernacular Language Support:** Native support for 12+ Indian languages including Tamil, Telugu, Hindi, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Assamese, and Urdu.
- **Code-Mixed Speech Handling:** Built-in routing for mixed dialects common in India (Hinglish, Tunglish, Tanglish, Kanglish).
- **Automatic Language Detection:** When language is omitted or set to `auto`, the engine automatically identifies the spoken language.
- **Micro-Banking Domain Bias:** Optimized prompting for financial domain terms (Jan Dhan, Mudra loan, KCC, DBT, Passbook, Balance check, IFSC, etc.).
- **Resilient API:** Automatically sanitizes Swagger UI / form placeholders (`string`, `null`, empty values).

---

## 🛠 Tech Stack

- **Framework:** FastAPI (Python 3.10+)
- **Server:** Uvicorn
- **ASR Inference:** Groq Cloud (`whisper-large-v3-turbo`)
- **Data Validation:** Pydantic v2

---

## 📦 Installation & Setup

### 1. Clone Repository & Navigate to Directory

```bash
git clone <repository-url>
cd RIT_HACKATHON
```

### 2. Create and Activate Virtual Environment (Recommended)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Groq API Key

Set your Groq API key in your environment:

```bash
# Windows (PowerShell)
$env:GROQ_API_KEY="your_groq_api_key_here"

# Windows (CMD)
set GROQ_API_KEY=your_groq_api_key_here

# Linux / macOS
export GROQ_API_KEY="your_groq_api_key_here"
```

*(Alternatively, the key can be defined in `ASR/asr_server.py` line 35).*

---

## 🏃 Running the Server

Navigate into the `ASR` folder and start the server:

```bash
cd ASR
python asr_server.py
```

Or run directly with Uvicorn:

```bash
python -m uvicorn asr_server:app --host 127.0.0.1 --port 8001 --reload
```

- **Live Server URL:** `http://127.0.0.1:8001`
- **Interactive Swagger Documentation:** `http://127.0.0.1:8001/docs`
- **Health Check:** `http://127.0.0.1:8001/health`

---

## 🌐 Language Support Matrix

| Language | ISO Code | Full Name | Code-Mixed Alias | Script Output |
| :--- | :--- | :--- | :--- | :--- |
| **Tamil** | `ta` | `tamil` | `tanglish` | தமிழ் (Tamil) / Roman |
| **Telugu** | `te` | `telugu` | `tunglish` | తెలుగు (Telugu) / Roman |
| **Hindi** | `hi` | `hindi` | `hinglish` | हिन्दी (Devanagari) / Roman |
| **Kannada** | `kn` | `kannada` | `kanglish` | ಕನ್ನಡ (Kannada) / Roman |
| **Malayalam** | `ml` | `malayalam` | — | മലയാളം (Malayalam) |
| **Bengali** | `bn` | `bengali` | — | বাংলা (Bengali) |
| **Marathi** | `mr` | `marathi` | — | मराठी (Devanagari) |
| **Gujarati** | `gu` | `gujarati` | — | ગુજરાતી (Gujarati) |
| **Punjabi** | `pa` | `punjabi` | — | ਪੰਜਾਬੀ (Gurmukhi) |
| **Assamese** | `as` | `assamese` | — | অসমীয়া (Assamese) |
| **Urdu** | `ur` | `urdu` | — | اردو (Perso-Arabic) |
| **English** | `en` | `english` | — | English (Latin) |

> **Note on Odia (`or`):** Odia is not part of Whisper's vocabulary. If Odia audio is needed, use an Indic-specific service such as AI4Bharat IndicConformer or Bhashini.

---

## 📡 API Endpoints

### 1. Transcribe Audio
- **Endpoint:** `POST /api/v1/transcribe`
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file` *(Required)*: Audio file (`.mp3`, `.wav`, `.webm`, `.ogg`, `.m4a`)
  - `language` *(Optional)*: ISO code (`ta`, `te`, `hi`, `en`), full name (`tamil`), or alias (`tanglish`, `hinglish`). Leave empty or pass `"auto"` for automatic detection.
  - `session_id` *(Optional)*: Session UUID for tracing. Automatically generated if omitted.

#### Sample Request (`curl`):

```bash
curl -X POST "http://127.0.0.1:8001/api/v1/transcribe" \
  -F "file=@sample_audio.mp3" \
  -F "language=ta"
```

#### Sample Response:

```json
{
  "session_id": "c9bf9e57-1685-4c89-bafb-ff5af830be8a",
  "text": "எனது வங்கி கணக்கு இருப்பு விவரம் பார்க்க வேண்டும்",
  "confidence": 0.94,
  "language": "Tamil",
  "audio_duration_ms": 2400,
  "timestamp": "2026-09-10T11:45:00.123456+00:00"
}
```

### 2. Supported Languages List
- **Endpoint:** `GET /api/v1/languages`
- Returns dictionary of all supported languages, full name mappings, and code-mixed aliases.

### 3. Health Check
- **Endpoint:** `GET /health`
- Returns server status and Groq API initialization state:
  ```json
  {"status": "healthy", "groq_api_configured": true}
  ```

---

## 💻 Python Client Example

```python
import requests

url = "http://127.0.0.1:8001/api/v1/transcribe"

with open("speech.mp3", "rb") as f:
    files = {"file": ("speech.mp3", f, "audio/mpeg")}
    data = {"language": "tamil"}  # Or "tanglish", "auto", or omit
    response = requests.post(url, files=files, data=data)

result = response.json()
print("Transcribed Text:", result["text"])
print("Detected Language:", result["language"])
```

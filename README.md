# Voice Banking App Frontend 🎙️

A fully functional, backend-agnostic frontend implementation of a voice-first banking assistant, built with Android Jetpack Compose and Kotlin. 

This repository contains the "Plug-and-Play" Android client. It handles all UI, audio recording, audio playback, state management, and user interaction. It expects to communicate with a remote AI backend.

---

## 🔌 How to Integrate (Plug-in) Your Backend

This frontend is designed to be completely decoupled from the backend logic. You can connect it to *any* backend (Python/FastAPI, Node.js, Java/Spring, etc.) as long as your backend adheres to the API contract.

### 1. Switch out of Demo Mode
By default, the app runs an offline scripted demo. To connect it to your live backend:
1. Open `app/build.gradle.kts`.
2. Change `DEMO_MODE` to `false`:
   ```kotlin
   buildConfigField("boolean", "DEMO_MODE", "false")
   ```
3. Update the `BASE_URL` to point to your backend server (e.g., your local IP or a deployed URL):
   ```kotlin
   buildConfigField("String", "BASE_URL", "\"http://192.168.1.100:8000/\"")
   ```

### 2. Implement the Backend API Contract
Your backend must expose the following **four** POST endpoints:

#### A. Send Voice
* **Endpoint:** `POST /api/v1/conversation/voice`
* **Content-Type:** `multipart/form-data`
* **Payload:**
  * `audio`: The recorded audio file (16kHz mono AAC `.m4a`).
  * `session_id`: (String) Unique session identifier.
  * `user_id`: (String) Hardcoded to "USER_123" for now.
  * `language`: (String) e.g., "ENGLISH", "TAMIL", "HINDI".

#### B. Send Text
* **Endpoint:** `POST /api/v1/conversation/text`
* **Content-Type:** `application/json`
* **Payload:** `{"text": "What is my balance?", "session_id": "...", "user_id": "...", "language": "..."}`

#### C. Confirm Action
* **Endpoint:** `POST /api/v1/conversation/confirm`
* **Content-Type:** `application/json`
* **Payload:** `{"action": "CONFIRM", "session_id": "..."}`

#### D. Cancel Action
* **Endpoint:** `POST /api/v1/conversation/cancel`
* **Content-Type:** `application/json`
* **Payload:** `{"action": "CANCEL", "session_id": "..."}`

### 3. Return the Expected JSON Response format
For *every* endpoint above, your backend must return an `AgentResponseDto` JSON object. The frontend uses the `response_type` field to decide exactly which UI card to draw. 

**Standard Response Schema:**
```json
{
  "session_id": "string",
  "response_type": "TEXT | BALANCE | TRANSACTIONS | CONFIRMATION | LOAN_PROGRESS | CONFLICT | SUCCESS | ERROR",
  "text": "The spoken/written text the assistant should reply with",
  "requires_confirmation": false,
  "audio_url": "Optional URL to pre-generated TTS audio",
  "payload": { ... } // Varies depending on response_type
}
```

#### Payload Examples by `response_type`:

* **`BALANCE`**:
  ```json
  "payload": { "account_type": "Savings", "balance": 12540, "currency": "INR", "masked_account_number": "XXXX 1234" }
  ```
* **`TRANSACTIONS`**:
  ```json
  "payload": { "transactions": [ { "id": "1", "date": "10 Sep", "description": "Amazon", "amount": 500, "type": "DEBIT", "status": "COMPLETED" } ] }
  ```
* **`CONFIRMATION`** (Prompts user with a Yes/No UI):
  ```json
  "requires_confirmation": true,
  "payload": { "action": "Deposit", "amount": 5000, "account_type": "Savings" }
  ```
* **`CONFLICT`** (Shows document mismatch UI):
  ```json
  "payload": { "field": "Full Name", "source_a": "PAN", "value_a": "Ramesh Kumar", "source_b": "Aadhaar", "value_b": "Ramesh K Singh" }
  ```
* **`LOAN_PROGRESS`** (Shows progress bar):
  ```json
  "payload": { "loan_type": "Mudra Loan", "completed_fields": 17, "total_fields": 22, "remaining_questions": 5, "current_question": "What is the business purpose?" }
  ```

---

## 🛠️ Architecture
* **Clean Architecture** (Domain -> Data -> UI)
* **Jetpack Compose** for entirely declarative UI.
* **Coroutines + Flow** for asynchronous events and state management.
* **Retrofit2** for API communications.

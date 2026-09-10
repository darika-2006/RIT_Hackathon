# Voice Banking Project 🎙️🏦

This repository contains the complete implementation for a Voice-First Banking Assistant, built for the hackathon. It consists of two main components:
1. **Frontend (Android App):** A plug-and-play voice interface built with Jetpack Compose.
2. **Backend (Database Schema):** A complete PostgreSQL relational schema simulating a multi-service retail bank.

---

## Part 1: Voice Banking App Frontend (Android)

A fully functional, backend-agnostic frontend implementation of a voice-first banking assistant, built with Android Jetpack Compose and Kotlin. 

This handles all UI, audio recording, audio playback, state management, and user interaction. It expects to communicate with a remote AI backend.

### 🔌 How to Integrate (Plug-in) Your Backend

This frontend is designed to be completely decoupled from the backend logic. You can connect it to *any* backend (Python/FastAPI, Node.js, Java/Spring, etc.) as long as your backend adheres to the API contract.

#### 1. Switch out of Demo Mode
By default, the app runs an offline scripted demo. To connect it to your live backend:
1. Open `app/build.gradle.kts`.
2. Change `DEMO_MODE` to `false`.
3. Update the `BASE_URL` to point to your backend server (e.g., your local IP or a deployed URL).

#### 2. Implement the Backend API Contract
Your backend must expose the following **four** POST endpoints:

* **Send Voice** (`POST /api/v1/conversation/voice`) - `multipart/form-data` with `audio`, `session_id`, `user_id`, `language`.
* **Send Text** (`POST /api/v1/conversation/text`) - JSON payload with `text`, `session_id`, `user_id`, `language`.
* **Confirm Action** (`POST /api/v1/conversation/confirm`) - JSON payload.
* **Cancel Action** (`POST /api/v1/conversation/cancel`) - JSON payload.

#### 3. Return the Expected JSON Response format
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

---

## Part 2: Bank Database Simulation — PostgreSQL

A complete relational schema simulating a multi-service retail bank: core banking, loans, deposits, insurance, pension, government schemes, and support/security — built for a hackathon.

### Files

| File | Purpose |
|---|---|
| `data.sql` | Linked sample data (customers) across every table, for demos |
| `table.sql` | All tables, constraints, foreign keys, and indexes |
| `README.md` | This file |

### Setup

```bash
createdb bank_sim
psql -d bank_sim -f table.sql
psql -d bank_sim -f data.sql
```

Requires PostgreSQL 13+. The schema uses the `pgcrypto` extension for `gen_random_uuid()`, which the script enables automatically. All primary keys are UUIDs rather than integers.

### Module map

The tables are grouped into functional domains:
1. **Auth / User**: `customers`, `device_sessions`
2. **Banking (core)**: `accounts`, `beneficiaries`, `transactions`
3. **Credit**: `loan_products` → `loan_applications` → `loans` → `loan_repayments`.
4. **Savings**: `deposit_products` → `deposits`.
5. **Insurance**: `insurance_products` → `insurance_policies`.
6. **Pension**: `pension_products` → `pension_accounts`.
7. **Government schemes**: `government_schemes` → `government_benefits`.
8. **Support / Security**: `complaints`, `audit_logs`, `notifications`.

### Design choices worth knowing
- **UUID primary keys** everywhere, generated via `gen_random_uuid()`. 
- **CHECK constraints** are used in place of Postgres ENUM types for all status/type fields.
- **ON DELETE CASCADE** is used from `customers` down to their owned rows.
- **loan_repayments.transaction_id** and **complaints.transaction_id** are nullable FKs to `transactions`.

### Extending this for a hackathon demo
- If you're wiring up an AI agent (the `audit_logs` table is built for this), have every tool call insert a row with `agent_name`, `intent`, `tool_called`, and `result` — that gives you a free activity trail to show judges.

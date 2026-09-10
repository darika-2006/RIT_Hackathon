package com.rit.voicebanking.data.remote

import com.google.gson.annotations.SerializedName

/**
 * Data Transfer Objects matching the backend JSON contract.
 *
 * ──────────────────────────────────────────────
 * BACKEND TEAM — API CONTRACT (v1)
 * ──────────────────────────────────────────────
 *
 * POST /api/v1/conversation/voice
 *   Multipart form: audio (WAV/PCM file), session_id, user_id, language
 *
 * POST /api/v1/conversation/text
 *   JSON body: AgentRequestDto
 *
 * POST /api/v1/conversation/confirm
 *   JSON body: { "session_id": "...", "action": "CONFIRM" | "CANCEL" }
 *
 * All endpoints return: AgentResponseDto
 * ──────────────────────────────────────────────
 *
 * These DTOs are isolated in the data/remote layer.
 * The domain layer never sees raw JSON — use AgentResponseMapper to convert.
 */

data class AgentRequestDto(
    @SerializedName("text") val text: String,
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("user_id") val userId: String = "demo_user",
    @SerializedName("language") val language: String
)

data class ConfirmRequestDto(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("action") val action: String  // "CONFIRM" | "CANCEL"
)

/**
 * Top-level response from all backend conversation endpoints.
 */
data class AgentResponseDto(
    @SerializedName("session_id") val sessionId: String = "",
    @SerializedName("response_type") val responseType: String = "TEXT",
    @SerializedName("text") val text: String = "",
    @SerializedName("language") val language: String = "en",
    @SerializedName("tts_audio_url") val ttsAudioUrl: String? = null,
    @SerializedName("tts_audio_base64") val ttsAudioBase64: String? = null,
    @SerializedName("requires_confirmation") val requiresConfirmation: Boolean = false,
    @SerializedName("action") val action: String? = null,
    @SerializedName("payload") val payload: PayloadDto? = null,
    @SerializedName("metadata") val metadata: Map<String, Any>? = null
)

/**
 * Flexible payload container — fields are nullable since only relevant
 * fields will be populated depending on response_type.
 */
data class PayloadDto(
    // BALANCE
    @SerializedName("account_type") val accountType: String? = null,
    @SerializedName("balance") val balance: Long? = null,
    @SerializedName("currency") val currency: String? = null,
    @SerializedName("masked_account_number") val maskedAccountNumber: String? = null,

    // TRANSACTIONS
    @SerializedName("transactions") val transactions: List<TransactionDto>? = null,

    // CONFIRMATION
    @SerializedName("amount") val amount: Long? = null,

    // LOAN_PROGRESS
    @SerializedName("loan_type") val loanType: String? = null,
    @SerializedName("completed_fields") val completedFields: Int? = null,
    @SerializedName("total_fields") val totalFields: Int? = null,
    @SerializedName("remaining_questions") val remainingQuestions: Int? = null,
    @SerializedName("current_question") val currentQuestion: String? = null,
    @SerializedName("current_question_index") val currentQuestionIndex: Int? = null,

    // LOAN_APPLICATION / SCHEME_INFO
    @SerializedName("scheme_name") val schemeName: String? = null,
    @SerializedName("max_amount") val maxAmount: Long? = null,
    @SerializedName("interest_rate") val interestRate: String? = null,
    @SerializedName("tenure") val tenure: String? = null,
    @SerializedName("eligibility") val eligibility: String? = null,
    @SerializedName("description") val description: String? = null,
    @SerializedName("key_benefits") val keyBenefits: List<String>? = null,

    // CONFLICT
    @SerializedName("field") val field: String? = null,
    @SerializedName("source_a") val sourceA: String? = null,
    @SerializedName("value_a") val valueA: String? = null,
    @SerializedName("source_b") val sourceB: String? = null,
    @SerializedName("value_b") val valueB: String? = null,

    // SUCCESS
    @SerializedName("reference_id") val referenceId: String? = null
)

data class TransactionDto(
    @SerializedName("id") val id: String = "",
    @SerializedName("amount") val amount: Long = 0,
    @SerializedName("currency") val currency: String = "INR",
    @SerializedName("type") val type: String = "DEBIT",
    @SerializedName("description") val description: String = "",
    @SerializedName("merchant") val merchant: String = "",
    @SerializedName("date") val date: String = "",
    @SerializedName("status") val status: String = "COMPLETED"
)

/**
 * Direct response from the Vernacular ASR Engine (/api/v1/transcribe)
 */
data class AsrResponseDto(
    @SerializedName("session_id") val sessionId: String = "",
    @SerializedName("text") val text: String = "",
    @SerializedName("confidence") val confidence: Float = 0f,
    @SerializedName("language") val language: String = "",
    @SerializedName("audio_duration_ms") val audioDurationMs: Long = 0,
    @SerializedName("timestamp") val timestamp: String = ""
)


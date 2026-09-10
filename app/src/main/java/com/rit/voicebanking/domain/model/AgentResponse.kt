package com.rit.voicebanking.domain.model

/**
 * Sealed interface representing every structured response the backend can return.
 *
 * The UI layer inspects the concrete type and delegates to the correct card component.
 * Android NEVER calculates or modifies these values — it only renders what the backend sends.
 */
sealed interface AgentResponse {

    /** A plain text reply from the assistant. */
    data class Text(
        val message: String,
        val sessionId: String = "",
        val language: String = "en"
    ) : AgentResponse

    /** Account balance response. */
    data class Balance(
        val accountType: String,
        val balance: Long,
        val currency: String = "INR",
        val maskedAccountNumber: String = "",
        val message: String = "",
        val sessionId: String = ""
    ) : AgentResponse

    /** List of recent transactions. */
    data class Transactions(
        val transactions: List<Transaction>,
        val message: String = "",
        val sessionId: String = ""
    ) : AgentResponse

    /** Detail of a single transaction. */
    data class TransactionDetail(
        val transaction: Transaction,
        val message: String = "",
        val sessionId: String = ""
    ) : AgentResponse

    /**
     * Confirmation required for a sensitive banking operation.
     * Frontend MUST NOT decide when confirmation is needed —
     * backend drives this via requires_confirmation.
     */
    data class Confirmation(
        val action: String,
        val amount: Long? = null,
        val currency: String = "INR",
        val accountType: String = "",
        val message: String,
        val sessionId: String = ""
    ) : AgentResponse

    /** Progress state during a multi-step loan application conversation. */
    data class LoanProgress(
        val loanType: String,
        val completedFields: Int,
        val totalFields: Int,
        val remainingQuestions: Int,
        val currentQuestion: String = "",
        val currentQuestionIndex: Int = 0,
        val message: String = "",
        val sessionId: String = ""
    ) : AgentResponse

    /** Loan application summary / scheme information. */
    data class LoanApplication(
        val schemeName: String,
        val maxAmount: Long,
        val interestRate: String,
        val tenure: String,
        val eligibility: String,
        val message: String = "",
        val sessionId: String = ""
    ) : AgentResponse

    /** Document conflict detected by backend (e.g. name mismatch between PAN and Aadhaar). */
    data class Conflict(
        val field: String,
        val sourceA: String,
        val valueA: String,
        val sourceB: String,
        val valueB: String,
        val message: String = "",
        val sessionId: String = ""
    ) : AgentResponse

    /** Government scheme / banking product information. */
    data class SchemeInfo(
        val schemeName: String,
        val description: String,
        val keyBenefits: List<String>,
        val message: String = "",
        val sessionId: String = ""
    ) : AgentResponse

    /** Terminal success for a completed operation. */
    data class Success(
        val message: String,
        val referenceId: String = "",
        val amount: Long? = null,
        val currency: String = "INR",
        val sessionId: String = ""
    ) : AgentResponse

    /** Error from backend or network layer. */
    data class Error(
        val message: String,
        val retryable: Boolean = true,
        val errorCode: String = "",
        val sessionId: String = ""
    ) : AgentResponse

    /** Transient loading/processing state (used internally by UI, not usually from backend). */
    object Loading : AgentResponse
}

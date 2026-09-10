package com.rit.voicebanking.data.repository

import com.rit.voicebanking.domain.model.AgentResponse
import com.rit.voicebanking.domain.model.Language
import com.rit.voicebanking.domain.model.Transaction
import com.rit.voicebanking.domain.model.TransactionStatus
import com.rit.voicebanking.domain.model.TransactionType
import com.rit.voicebanking.domain.repository.BankingRepository
import kotlinx.coroutines.delay
import java.io.File

/**
 * Demo implementation of [BankingRepository].
 *
 * Produces realistic scripted responses WITHOUT any real backend.
 * Used when BuildConfig.DEMO_MODE = true.
 *
 * The UI behaves identically to production — it cannot tell the difference.
 * All fake banking values are synthetic demo data, not real calculations.
 *
 * Demo flow sequence follows the hackathon demo script:
 * 1. Balance query
 * 2. Transactions query
 * 3. Loan conversation (multi-turn)
 * 4. Conflict detection
 * 5. Confirmation
 * 6. Success
 */
class DemoBankingRepository : BankingRepository {

    private var turnCount = 0
    private var inLoanFlow = false
    private var loanTurn = 0
    private var pendingConfirmation = false

    override suspend fun sendVoice(
        audioFile: File,
        sessionId: String,
        language: Language
    ): AgentResponse {
        delay(1500) // simulate ASR + processing time
        return getNextDemoResponse(sessionId)
    }

    override suspend fun sendText(
        text: String,
        sessionId: String,
        language: Language
    ): AgentResponse {
        delay(800) // simulate processing
        val lowerText = text.lowercase()

        return when {
            lowerText.contains("balance") || lowerText.contains("பணம்") ||
                    lowerText.contains("शेष") -> getDemoBalance(sessionId)

            lowerText.contains("transaction") || lowerText.contains("history") ||
                    lowerText.contains("காட்டு") -> getDemoTransactions(sessionId)

            lowerText.contains("loan") || lowerText.contains("கடன்") ||
                    lowerText.contains("ऋण") || lowerText.contains("mudra") -> {
                inLoanFlow = true
                loanTurn = 0
                getDemoLoanStart(sessionId)
            }

            inLoanFlow -> {
                loanTurn++
                getDemoLoanTurn(sessionId)
            }

            lowerText.contains("deposit") || lowerText.contains("save") -> {
                pendingConfirmation = true
                getDemoConfirmation(sessionId)
            }

            lowerText.contains("scheme") || lowerText.contains("pm") -> getDemoSchemeInfo(sessionId)

            else -> getNextDemoResponse(sessionId)
        }
    }

    override suspend fun confirm(sessionId: String): AgentResponse {
        delay(1200)
        pendingConfirmation = false
        return AgentResponse.Success(
            message = "Transaction completed successfully. ₹5,000 has been deposited to your Savings Account.",
            referenceId = "TXN${System.currentTimeMillis()}",
            amount = 5000L,
            currency = "INR",
            sessionId = sessionId
        )
    }

    override suspend fun cancel(sessionId: String): AgentResponse {
        delay(300)
        pendingConfirmation = false
        inLoanFlow = false
        loanTurn = 0
        return AgentResponse.Text(
            message = "No problem. Transaction cancelled. What else can I help you with?",
            sessionId = sessionId
        )
    }

    // ─── Private demo response builders ───────────────────────────────────────

    private fun getNextDemoResponse(sessionId: String): AgentResponse {
        turnCount++
        return when (turnCount % 6) {
            1 -> getDemoBalance(sessionId)
            2 -> getDemoTransactions(sessionId)
            3 -> {
                inLoanFlow = true
                loanTurn = 0
                getDemoLoanStart(sessionId)
            }
            4 -> getDemoConflict(sessionId)
            5 -> getDemoConfirmation(sessionId)
            else -> AgentResponse.Text(
                message = "Hello! I'm your banking assistant. You can ask me about your balance, transactions, or apply for a loan.",
                sessionId = sessionId
            )
        }
    }

    private fun getDemoBalance(sessionId: String) = AgentResponse.Balance(
        accountType = "Savings Account",
        balance = 12540L,
        currency = "INR",
        maskedAccountNumber = "XXXX XXXX 4821",
        message = "Your savings account balance is ₹12,540.",
        sessionId = sessionId
    )

    private fun getDemoTransactions(sessionId: String) = AgentResponse.Transactions(
        transactions = listOf(
            Transaction(
                id = "T001",
                amount = 5000L,
                currency = "INR",
                type = TransactionType.CREDIT,
                description = "Salary Credit",
                merchant = "Employer",
                date = "10 Sep 2026",
                status = TransactionStatus.COMPLETED
            ),
            Transaction(
                id = "T002",
                amount = 450L,
                currency = "INR",
                type = TransactionType.DEBIT,
                description = "Electricity Bill",
                merchant = "TNEB",
                date = "09 Sep 2026",
                status = TransactionStatus.COMPLETED
            ),
            Transaction(
                id = "T003",
                amount = 200L,
                currency = "INR",
                type = TransactionType.DEBIT,
                description = "Mobile Recharge",
                merchant = "Airtel",
                date = "08 Sep 2026",
                status = TransactionStatus.COMPLETED
            ),
            Transaction(
                id = "T004",
                amount = 1200L,
                currency = "INR",
                type = TransactionType.DEBIT,
                description = "Grocery Shopping",
                merchant = "DMart",
                date = "07 Sep 2026",
                status = TransactionStatus.COMPLETED
            ),
            Transaction(
                id = "T005",
                amount = 3000L,
                currency = "INR",
                type = TransactionType.CREDIT,
                description = "UPI Received",
                merchant = "Ramesh Kumar",
                date = "06 Sep 2026",
                status = TransactionStatus.COMPLETED
            )
        ),
        message = "Here are your recent transactions.",
        sessionId = sessionId
    )

    private fun getDemoLoanStart(sessionId: String) = AgentResponse.LoanProgress(
        loanType = "PM Mudra Loan",
        completedFields = 17,
        totalFields = 22,
        remainingQuestions = 5,
        currentQuestion = "What is the purpose of your loan? (e.g., business expansion, working capital, equipment purchase)",
        currentQuestionIndex = 1,
        message = "Great! I can help you apply for a PM Mudra Loan. I already have 17 of your details. I just need to ask you 5 more questions.",
        sessionId = sessionId
    )

    private fun getDemoLoanTurn(sessionId: String): AgentResponse {
        return when (loanTurn) {
            1 -> AgentResponse.LoanProgress(
                loanType = "PM Mudra Loan",
                completedFields = 18,
                totalFields = 22,
                remainingQuestions = 4,
                currentQuestion = "How much loan amount do you need? (Maximum ₹10 lakhs under Tarun category)",
                currentQuestionIndex = 2,
                message = "Thank you. How much loan amount do you need?",
                sessionId = sessionId
            )
            2 -> AgentResponse.LoanProgress(
                loanType = "PM Mudra Loan",
                completedFields = 19,
                totalFields = 22,
                remainingQuestions = 3,
                currentQuestion = "What is the name of your business?",
                currentQuestionIndex = 3,
                message = "Got it. What is the name of your business?",
                sessionId = sessionId
            )
            3 -> {
                // Trigger conflict
                inLoanFlow = false
                getDemoConflict(sessionId)
            }
            else -> getDemoConfirmation(sessionId)
        }
    }

    private fun getDemoConflict(sessionId: String) = AgentResponse.Conflict(
        field = "Full Name",
        sourceA = "PAN Card",
        valueA = "Ramesh Kumar",
        sourceB = "Aadhaar Card",
        valueB = "Ramesh Kumar Singh",
        message = "I found a mismatch in your documents. Your name differs between your PAN and Aadhaar. This may affect your application.",
        sessionId = sessionId
    )

    private fun getDemoConfirmation(sessionId: String) = AgentResponse.Confirmation(
        action = "Deposit",
        amount = 5000L,
        currency = "INR",
        accountType = "Savings Account",
        message = "You are about to deposit ₹5,000 into your Savings Account. Should I proceed?",
        sessionId = sessionId
    )

    private fun getDemoSchemeInfo(sessionId: String) = AgentResponse.SchemeInfo(
        schemeName = "PM Mudra Yojana",
        description = "Pradhan Mantri MUDRA Yojana provides micro-finance support to small and micro enterprises.",
        keyBenefits = listOf(
            "Loans up to ₹10 lakhs",
            "No collateral required",
            "Competitive interest rates",
            "Quick disbursement",
            "Available for new and existing businesses"
        ),
        message = "Here's information about PM Mudra Yojana.",
        sessionId = sessionId
    )
}

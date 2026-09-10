package com.rit.voicebanking.data.remote

import com.rit.voicebanking.domain.model.AgentResponse
import com.rit.voicebanking.domain.model.Transaction
import com.rit.voicebanking.domain.model.TransactionStatus
import com.rit.voicebanking.domain.model.TransactionType

/**
 * Maps backend DTOs → domain models.
 * All mapping logic is centralized here, keeping domain and UI clean.
 */
object AgentResponseMapper {

    fun toDomain(dto: AgentResponseDto): AgentResponse {
        val payload = dto.payload
        val text = dto.text
        val sessionId = dto.sessionId

        return when (dto.responseType.uppercase()) {
            "BALANCE" -> AgentResponse.Balance(
                accountType = payload?.accountType ?: "Savings Account",
                balance = payload?.balance ?: 0L,
                currency = payload?.currency ?: "INR",
                maskedAccountNumber = payload?.maskedAccountNumber ?: "",
                message = text,
                sessionId = sessionId
            )

            "TRANSACTIONS" -> AgentResponse.Transactions(
                transactions = payload?.transactions?.map { mapTransaction(it) } ?: emptyList(),
                message = text,
                sessionId = sessionId
            )

            "TRANSACTION_DETAIL" -> {
                val tx = payload?.transactions?.firstOrNull()
                if (tx != null) {
                    AgentResponse.TransactionDetail(
                        transaction = mapTransaction(tx),
                        message = text,
                        sessionId = sessionId
                    )
                } else {
                    AgentResponse.Text(text, sessionId)
                }
            }

            "CONFIRMATION" -> AgentResponse.Confirmation(
                action = payload?.schemeName ?: dto.action ?: "Transaction",
                amount = payload?.amount,
                currency = payload?.currency ?: "INR",
                accountType = payload?.accountType ?: "",
                message = text,
                sessionId = sessionId
            )

            "LOAN_PROGRESS" -> AgentResponse.LoanProgress(
                loanType = payload?.loanType ?: "Loan",
                completedFields = payload?.completedFields ?: 0,
                totalFields = payload?.totalFields ?: 0,
                remainingQuestions = payload?.remainingQuestions ?: 0,
                currentQuestion = payload?.currentQuestion ?: text,
                currentQuestionIndex = payload?.currentQuestionIndex ?: 0,
                message = text,
                sessionId = sessionId
            )

            "LOAN_APPLICATION" -> AgentResponse.LoanApplication(
                schemeName = payload?.schemeName ?: "Mudra Loan",
                maxAmount = payload?.maxAmount ?: 0L,
                interestRate = payload?.interestRate ?: "",
                tenure = payload?.tenure ?: "",
                eligibility = payload?.eligibility ?: "",
                message = text,
                sessionId = sessionId
            )

            "CONFLICT" -> AgentResponse.Conflict(
                field = payload?.field ?: "Name",
                sourceA = payload?.sourceA ?: "PAN",
                valueA = payload?.valueA ?: "",
                sourceB = payload?.sourceB ?: "Aadhaar",
                valueB = payload?.valueB ?: "",
                message = text,
                sessionId = sessionId
            )

            "SCHEME_INFO" -> AgentResponse.SchemeInfo(
                schemeName = payload?.schemeName ?: "",
                description = payload?.description ?: "",
                keyBenefits = payload?.keyBenefits ?: emptyList(),
                message = text,
                sessionId = sessionId
            )

            "SUCCESS" -> AgentResponse.Success(
                message = text,
                referenceId = payload?.referenceId ?: "",
                amount = payload?.amount,
                currency = payload?.currency ?: "INR",
                sessionId = sessionId
            )

            "ERROR" -> AgentResponse.Error(
                message = text.ifEmpty { "Something went wrong. Please try again." },
                retryable = true,
                sessionId = sessionId
            )

            else -> AgentResponse.Text(text, sessionId)
        }
    }

    private fun mapTransaction(dto: TransactionDto): Transaction = Transaction(
        id = dto.id,
        amount = dto.amount,
        currency = dto.currency,
        type = when (dto.type.uppercase()) {
            "CREDIT" -> TransactionType.CREDIT
            else -> TransactionType.DEBIT
        },
        description = dto.description,
        merchant = dto.merchant,
        date = dto.date,
        status = when (dto.status.uppercase()) {
            "PENDING" -> TransactionStatus.PENDING
            "FAILED" -> TransactionStatus.FAILED
            "REVERSED" -> TransactionStatus.REVERSED
            else -> TransactionStatus.COMPLETED
        }
    )
}

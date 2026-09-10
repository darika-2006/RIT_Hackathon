package com.rit.voicebanking

import com.rit.voicebanking.data.remote.AgentResponseDto
import com.rit.voicebanking.data.remote.AgentResponseMapper
import com.rit.voicebanking.data.remote.PayloadDto
import com.rit.voicebanking.domain.model.AgentResponse
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * Unit tests for AgentResponseMapper.
 * Verifies that backend DTOs are correctly mapped to domain models.
 */
class AgentResponseMapperTest {

    @Test
    fun `maps BALANCE response correctly`() {
        val dto = AgentResponseDto(
            sessionId = "S001",
            responseType = "BALANCE",
            text = "Your balance is ₹12,540",
            payload = PayloadDto(
                accountType = "Savings Account",
                balance = 12540L,
                currency = "INR",
                maskedAccountNumber = "XXXX 4821"
            )
        )

        val result = AgentResponseMapper.toDomain(dto)

        assertTrue(result is AgentResponse.Balance)
        val balance = result as AgentResponse.Balance
        assertEquals(12540L, balance.balance)
        assertEquals("Savings Account", balance.accountType)
        assertEquals("INR", balance.currency)
        assertEquals("XXXX 4821", balance.maskedAccountNumber)
    }

    @Test
    fun `maps TEXT response correctly`() {
        val dto = AgentResponseDto(
            sessionId = "S001",
            responseType = "TEXT",
            text = "Hello! How can I help you?"
        )

        val result = AgentResponseMapper.toDomain(dto)

        assertTrue(result is AgentResponse.Text)
        assertEquals("Hello! How can I help you?", (result as AgentResponse.Text).message)
    }

    @Test
    fun `maps CONFIRMATION response correctly`() {
        val dto = AgentResponseDto(
            sessionId = "S001",
            responseType = "CONFIRMATION",
            text = "Confirm deposit of ₹5,000?",
            requiresConfirmation = true,
            payload = PayloadDto(
                amount = 5000L,
                currency = "INR",
                accountType = "Savings Account"
            )
        )

        val result = AgentResponseMapper.toDomain(dto)

        assertTrue(result is AgentResponse.Confirmation)
        val confirmation = result as AgentResponse.Confirmation
        assertEquals(5000L, confirmation.amount)
        assertEquals("INR", confirmation.currency)
        assertEquals("Savings Account", confirmation.accountType)
    }

    @Test
    fun `maps CONFLICT response correctly`() {
        val dto = AgentResponseDto(
            sessionId = "S001",
            responseType = "CONFLICT",
            text = "Name mismatch detected.",
            payload = PayloadDto(
                field = "Full Name",
                sourceA = "PAN",
                valueA = "Ramesh Kumar",
                sourceB = "Aadhaar",
                valueB = "Ramesh Kumar Singh"
            )
        )

        val result = AgentResponseMapper.toDomain(dto)

        assertTrue(result is AgentResponse.Conflict)
        val conflict = result as AgentResponse.Conflict
        assertEquals("Full Name", conflict.field)
        assertEquals("PAN", conflict.sourceA)
        assertEquals("Ramesh Kumar", conflict.valueA)
        assertEquals("Aadhaar", conflict.sourceB)
        assertEquals("Ramesh Kumar Singh", conflict.valueB)
    }

    @Test
    fun `maps LOAN_PROGRESS response correctly`() {
        val dto = AgentResponseDto(
            sessionId = "S001",
            responseType = "LOAN_PROGRESS",
            text = "What is the purpose of your loan?",
            payload = PayloadDto(
                loanType = "PM Mudra Loan",
                completedFields = 17,
                totalFields = 22,
                remainingQuestions = 5,
                currentQuestion = "What is the purpose of your loan?",
                currentQuestionIndex = 1
            )
        )

        val result = AgentResponseMapper.toDomain(dto)

        assertTrue(result is AgentResponse.LoanProgress)
        val loan = result as AgentResponse.LoanProgress
        assertEquals(17, loan.completedFields)
        assertEquals(22, loan.totalFields)
        assertEquals(5, loan.remainingQuestions)
        assertEquals("PM Mudra Loan", loan.loanType)
    }

    @Test
    fun `maps SUCCESS response correctly`() {
        val dto = AgentResponseDto(
            sessionId = "S001",
            responseType = "SUCCESS",
            text = "Transaction completed successfully.",
            payload = PayloadDto(
                referenceId = "TXN123",
                amount = 5000L
            )
        )

        val result = AgentResponseMapper.toDomain(dto)

        assertTrue(result is AgentResponse.Success)
        val success = result as AgentResponse.Success
        assertEquals("TXN123", success.referenceId)
        assertEquals(5000L, success.amount)
    }

    @Test
    fun `maps ERROR response with fallback message`() {
        val dto = AgentResponseDto(
            sessionId = "S001",
            responseType = "ERROR",
            text = ""
        )

        val result = AgentResponseMapper.toDomain(dto)

        assertTrue(result is AgentResponse.Error)
        val error = result as AgentResponse.Error
        assertTrue(error.message.isNotBlank())
        assertTrue(error.retryable)
    }

    @Test
    fun `maps unknown response_type as Text`() {
        val dto = AgentResponseDto(
            sessionId = "S001",
            responseType = "UNKNOWN_FUTURE_TYPE",
            text = "Some message"
        )

        val result = AgentResponseMapper.toDomain(dto)

        assertTrue(result is AgentResponse.Text)
    }
}

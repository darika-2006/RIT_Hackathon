package com.rit.voicebanking.domain.usecase

import com.rit.voicebanking.domain.model.AgentResponse
import com.rit.voicebanking.domain.model.Language
import com.rit.voicebanking.domain.repository.BankingRepository
import java.io.File

class SendVoiceUseCase(private val repository: BankingRepository) {
    suspend operator fun invoke(
        audioFile: File,
        sessionId: String,
        language: Language
    ): AgentResponse = repository.sendVoice(audioFile, sessionId, language)
}

class SendTextUseCase(private val repository: BankingRepository) {
    suspend operator fun invoke(
        text: String,
        sessionId: String,
        language: Language
    ): AgentResponse = repository.sendText(text, sessionId, language)
}

class ConfirmUseCase(private val repository: BankingRepository) {
    suspend operator fun invoke(sessionId: String): AgentResponse =
        repository.confirm(sessionId)
}

class CancelUseCase(private val repository: BankingRepository) {
    suspend operator fun invoke(sessionId: String): AgentResponse =
        repository.cancel(sessionId)
}

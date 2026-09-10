package com.rit.voicebanking.domain.repository

import com.rit.voicebanking.domain.model.AgentResponse
import com.rit.voicebanking.domain.model.Language
import java.io.File

/**
 * The plug-in contract that isolates the frontend from any specific backend implementation.
 *
 * Concrete implementations:
 *   - [com.rit.voicebanking.data.repository.DemoBankingRepository] — demo/mock mode
 *   - [com.rit.voicebanking.data.repository.RemoteBankingRepository] — teammates' real backend
 *
 * The ViewModel/UseCase layer depends only on this interface.
 * Switching between demo and production is done at the DI / initialization layer (MainActivity).
 */
interface BankingRepository {

    /**
     * Send a recorded audio file to the backend for ASR + agent processing.
     *
     * @param audioFile  WAV/PCM file produced by AudioRecorder
     * @param sessionId  Current conversation session identifier
     * @param language   Active language for ASR and TTS
     * @return           Structured [AgentResponse] from the backend
     */
    suspend fun sendVoice(
        audioFile: File,
        sessionId: String,
        language: Language
    ): AgentResponse

    /**
     * Send a typed/text message to the backend agent.
     *
     * @param text       User's typed message
     * @param sessionId  Current conversation session identifier
     * @param language   Active language
     * @return           Structured [AgentResponse] from the backend
     */
    suspend fun sendText(
        text: String,
        sessionId: String,
        language: Language
    ): AgentResponse

    /**
     * Confirm a pending sensitive banking action.
     * Must only be called after the backend has returned [AgentResponse.Confirmation]
     * with requires_confirmation = true.
     *
     * @param sessionId  Current conversation session identifier
     * @return           Updated [AgentResponse] (typically Success or Error)
     */
    suspend fun confirm(sessionId: String): AgentResponse

    /**
     * Cancel a pending confirmation dialog.
     * Returns the app to a safe idle/conversation state.
     *
     * @param sessionId  Current conversation session identifier
     * @return           [AgentResponse] (typically Text acknowledging cancellation)
     */
    suspend fun cancel(sessionId: String): AgentResponse
}

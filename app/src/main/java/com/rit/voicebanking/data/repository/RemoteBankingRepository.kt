package com.rit.voicebanking.data.repository

import com.rit.voicebanking.data.remote.AgentRequestDto
import com.rit.voicebanking.data.remote.AgentResponseMapper
import com.rit.voicebanking.data.remote.ApiService
import com.rit.voicebanking.data.remote.ConfirmRequestDto
import com.rit.voicebanking.domain.model.AgentResponse
import com.rit.voicebanking.domain.model.Language
import com.rit.voicebanking.domain.repository.BankingRepository
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File

/**
 * Production implementation of [BankingRepository].
 * Communicates with teammates' backend via Retrofit/OkHttp.
 *
 * All network calls run on the calling coroutine dispatcher (IO expected from ViewModel).
 * Network errors are caught in the ViewModel and converted to [AgentResponse.Error].
 */
class RemoteBankingRepository(
    private val apiService: ApiService
) : BankingRepository {

    override suspend fun sendVoice(
        audioFile: File,
        sessionId: String,
        language: Language
    ): AgentResponse {
        val audioPart = MultipartBody.Part.createFormData(
            name = "audio",
            filename = audioFile.name,
            body = audioFile.asRequestBody("audio/wav".toMediaType())
        )
        val sessionPart = sessionId.toRequestBody("text/plain".toMediaType())
        val userIdPart = "demo_user".toRequestBody("text/plain".toMediaType())
        val langPart = language.code.toRequestBody("text/plain".toMediaType())

        val dto = apiService.sendVoice(audioPart, sessionPart, userIdPart, langPart)
        return AgentResponseMapper.toDomain(dto)
    }

    override suspend fun sendText(
        text: String,
        sessionId: String,
        language: Language
    ): AgentResponse {
        val request = AgentRequestDto(
            text = text,
            sessionId = sessionId,
            language = language.code
        )
        val dto = apiService.sendText(request)
        return AgentResponseMapper.toDomain(dto)
    }

    override suspend fun confirm(sessionId: String): AgentResponse {
        val dto = apiService.confirm(ConfirmRequestDto(sessionId, "CONFIRM"))
        return AgentResponseMapper.toDomain(dto)
    }

    override suspend fun cancel(sessionId: String): AgentResponse {
        val dto = apiService.cancel(ConfirmRequestDto(sessionId, "CANCEL"))
        return AgentResponseMapper.toDomain(dto)
    }
}

package com.rit.voicebanking.data.remote

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.*

/**
 * Retrofit API service interface.
 *
 * ──────────────────────────────────────────────
 * BACKEND TEAM INTEGRATION POINT
 * ──────────────────────────────────────────────
 * Base URL is configured in build.gradle.kts:
 *   buildConfigField("String", "BASE_URL", "\"http://10.0.2.2:8000/\"")
 *
 * 10.0.2.2 is the Android emulator loopback address for the host machine's localhost.
 * Change this to your actual server IP for device testing.
 * ──────────────────────────────────────────────
 */
interface ApiService {

    /**
     * Direct ASR call to transcribe recorded audio into text.
     */
    @Multipart
    @POST("api/v1/transcribe")
    suspend fun transcribeAudio(
        @Part file: MultipartBody.Part,
        @Part("language") language: RequestBody? = null,
        @Part("session_id") sessionId: RequestBody? = null
    ): AsrResponseDto

    /**
     * Send recorded voice audio for ASR → agent processing.
     * The backend handles speech recognition — Android only sends raw audio.
     */
    @Multipart
    @POST("api/v1/conversation/voice")
    suspend fun sendVoice(
        @Part audio: MultipartBody.Part,
        @Part("session_id") sessionId: RequestBody,
        @Part("user_id") userId: RequestBody,
        @Part("language") language: RequestBody
    ): AgentResponseDto

    /**
     * Send a text message (typed input or quick action) to the agent.
     */
    @POST("api/v1/conversation/text")
    suspend fun sendText(
        @Body request: AgentRequestDto
    ): AgentResponseDto

    /**
     * Confirm a pending banking action (e.g. confirm deposit).
     */
    @POST("api/v1/conversation/confirm")
    suspend fun confirm(
        @Body request: ConfirmRequestDto
    ): AgentResponseDto

    /**
     * Cancel a pending confirmation.
     */
    @POST("api/v1/conversation/cancel")
    suspend fun cancel(
        @Body request: ConfirmRequestDto
    ): AgentResponseDto
}

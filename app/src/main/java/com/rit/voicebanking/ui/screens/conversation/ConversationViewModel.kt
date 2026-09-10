package com.rit.voicebanking.ui.screens.conversation

import android.app.Application
import android.util.Log
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.rit.voicebanking.audio.AudioPlayer
import com.rit.voicebanking.audio.AudioRecorder
import com.rit.voicebanking.data.local.SessionStorage
import com.rit.voicebanking.domain.model.AgentResponse
import com.rit.voicebanking.domain.model.ConversationMessage
import com.rit.voicebanking.domain.model.Language
import com.rit.voicebanking.domain.model.Role
import com.rit.voicebanking.domain.repository.BankingRepository
import com.rit.voicebanking.domain.usecase.CancelUseCase
import com.rit.voicebanking.domain.usecase.ConfirmUseCase
import com.rit.voicebanking.domain.usecase.SendTextUseCase
import com.rit.voicebanking.domain.usecase.SendVoiceUseCase
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.UUID

/**
 * Sealed class representing the complete UI state machine.
 *
 * IDLE → LISTENING → RECORDING → UPLOADING → PROCESSING
 *      → DISPLAY_RESULT / WAITING_FOR_CONFIRMATION / LOAN_FLOW
 *      → SUCCESS / ERROR
 *
 * Never use disconnected Boolean flags for state — always use this sealed class.
 */
sealed class ConversationUiState {
    object Idle : ConversationUiState()
    object Listening : ConversationUiState()
    object Recording : ConversationUiState()
    object Uploading : ConversationUiState()
    object Processing : ConversationUiState()
    data class DisplayResult(val response: AgentResponse) : ConversationUiState()
    data class WaitingForConfirmation(val confirmation: AgentResponse.Confirmation) : ConversationUiState()
    data class Error(val message: String, val retryable: Boolean) : ConversationUiState()
    object Success : ConversationUiState()
}

/**
 * ViewModel for the entire conversation experience.
 *
 * Owns:
 * - UI state machine
 * - Conversation history
 * - Audio recording/playback lifecycle
 * - Backend communication (through use cases)
 *
 * The Composable layer observes StateFlow and emits events.
 * No business logic lives inside Composables.
 */
class ConversationViewModel(
    application: Application,
    private val repository: BankingRepository
) : AndroidViewModel(application) {

    // ─── State ────────────────────────────────────────────────────────────────

    private val _uiState = MutableStateFlow<ConversationUiState>(ConversationUiState.Idle)
    val uiState: StateFlow<ConversationUiState> = _uiState.asStateFlow()

    private val _messages = MutableStateFlow<List<ConversationMessage>>(emptyList())
    val messages: StateFlow<List<ConversationMessage>> = _messages.asStateFlow()

    private val _selectedLanguage = MutableStateFlow(Language.ENGLISH)
    val selectedLanguage: StateFlow<Language> = _selectedLanguage.asStateFlow()

    private val _lastTtsText = MutableStateFlow("")
    val lastTtsText: StateFlow<String> = _lastTtsText.asStateFlow()

    // ─── Infrastructure ───────────────────────────────────────────────────────

    private val sessionStorage = SessionStorage(application)
    private val audioRecorder = AudioRecorder(application)
    private val audioPlayer = AudioPlayer(application)

    private val sendVoiceUseCase = SendVoiceUseCase(repository)
    private val sendTextUseCase = SendTextUseCase(repository)
    private val confirmUseCase = ConfirmUseCase(repository)
    private val cancelUseCase = CancelUseCase(repository)

    private var currentSessionId: String = sessionStorage.sessionId

    // ─── Language ─────────────────────────────────────────────────────────────

    fun setLanguage(language: Language) {
        _selectedLanguage.value = language
        sessionStorage.languageCode = language.code
    }

    // ─── Voice recording ──────────────────────────────────────────────────────

    fun startListening() {
        if (_uiState.value !is ConversationUiState.Idle &&
            _uiState.value !is ConversationUiState.DisplayResult &&
            _uiState.value !is ConversationUiState.Error) return

        _uiState.value = ConversationUiState.Listening
        // Start recording immediately — "listening" is the visual state shown while mic opens
        val file = audioRecorder.startRecording()
        if (file != null) {
            _uiState.value = ConversationUiState.Recording
        } else {
            _uiState.value = ConversationUiState.Error(
                "Unable to access microphone. Please check permissions.",
                retryable = false
            )
        }
    }

    fun stopRecordingAndSend() {
        val audioFile = audioRecorder.stopRecording() ?: run {
            _uiState.value = ConversationUiState.Error("Recording failed. Please try again.", retryable = true)
            return
        }

        _uiState.value = ConversationUiState.Uploading

        viewModelScope.launch {
            try {
                _uiState.value = ConversationUiState.Processing
                val response = sendVoiceUseCase(audioFile, currentSessionId, _selectedLanguage.value)
                audioFile.delete() // clean up temp file
                handleResponse(response, inputText = "[Voice input]")
            } catch (e: Exception) {
                Log.e("ConversationVM", "Voice send failed", e)
                _uiState.value = ConversationUiState.Error(
                    friendlyError(e),
                    retryable = true
                )
            }
        }
    }

    fun cancelRecording() {
        audioRecorder.cancelRecording()
        _uiState.value = ConversationUiState.Idle
    }

    // ─── Text input ───────────────────────────────────────────────────────────

    fun sendText(text: String) {
        if (text.isBlank()) return

        addUserMessage(text)
        _uiState.value = ConversationUiState.Processing

        viewModelScope.launch {
            try {
                val response = sendTextUseCase(text, currentSessionId, _selectedLanguage.value)
                handleResponse(response, inputText = text)
            } catch (e: Exception) {
                Log.e("ConversationVM", "Text send failed", e)
                _uiState.value = ConversationUiState.Error(friendlyError(e), retryable = true)
            }
        }
    }

    // ─── Quick actions ────────────────────────────────────────────────────────

    fun sendQuickAction(action: String) = sendText(action)

    // ─── Confirmation ─────────────────────────────────────────────────────────

    fun confirmAction() {
        _uiState.value = ConversationUiState.Processing
        viewModelScope.launch {
            try {
                val response = confirmUseCase(currentSessionId)
                handleResponse(response, inputText = "Confirmed")
            } catch (e: Exception) {
                _uiState.value = ConversationUiState.Error(friendlyError(e), retryable = true)
            }
        }
    }

    fun cancelAction() {
        viewModelScope.launch {
            try {
                val response = cancelUseCase(currentSessionId)
                handleResponse(response, inputText = "Cancelled")
            } catch (e: Exception) {
                _uiState.value = ConversationUiState.Idle
            }
        }
    }

    // ─── TTS ─────────────────────────────────────────────────────────────────

    fun replayTts() {
        val text = _lastTtsText.value
        if (text.isNotBlank()) {
            audioPlayer.speak(text, _selectedLanguage.value)
        }
    }

    // ─── Error recovery ───────────────────────────────────────────────────────

    fun retry() {
        _uiState.value = ConversationUiState.Idle
    }

    fun goHome() {
        _uiState.value = ConversationUiState.Idle
        _messages.value = emptyList()
        currentSessionId = sessionStorage.newSession()
    }

    // ─── Private helpers ──────────────────────────────────────────────────────

    private fun handleResponse(response: AgentResponse, inputText: String) {
        when (response) {
            is AgentResponse.Confirmation -> {
                addAssistantMessage(response.message, response)
                _uiState.value = ConversationUiState.WaitingForConfirmation(response)
                speakText(response.message)
            }

            is AgentResponse.Success -> {
                addAssistantMessage(response.message, response)
                _uiState.value = ConversationUiState.Success
                speakText(response.message)
            }

            is AgentResponse.Error -> {
                val msg = response.message
                addAssistantMessage(msg, response)
                _uiState.value = ConversationUiState.Error(msg, response.retryable)
            }

            is AgentResponse.Loading -> {
                _uiState.value = ConversationUiState.Processing
            }

            else -> {
                val text = extractText(response)
                addAssistantMessage(text, response)
                _uiState.value = ConversationUiState.DisplayResult(response)
                speakText(text)
            }
        }
    }

    private fun addUserMessage(text: String) {
        val msg = ConversationMessage(
            id = UUID.randomUUID().toString(),
            role = Role.USER,
            text = text
        )
        _messages.value = _messages.value + msg
    }

    private fun addAssistantMessage(text: String, response: AgentResponse) {
        val msg = ConversationMessage(
            id = UUID.randomUUID().toString(),
            role = Role.ASSISTANT,
            text = text,
            response = response
        )
        _messages.value = _messages.value + msg
    }

    private fun speakText(text: String) {
        if (text.isNotBlank()) {
            _lastTtsText.value = text
            audioPlayer.speak(text, _selectedLanguage.value)
        }
    }

    private fun extractText(response: AgentResponse): String = when (response) {
        is AgentResponse.Text -> response.message
        is AgentResponse.Balance -> response.message.ifEmpty { "Your balance is ₹${response.balance}" }
        is AgentResponse.Transactions -> response.message.ifEmpty { "Here are your recent transactions." }
        is AgentResponse.TransactionDetail -> response.message
        is AgentResponse.LoanProgress -> response.message.ifEmpty { response.currentQuestion }
        is AgentResponse.LoanApplication -> response.message
        is AgentResponse.Conflict -> response.message
        is AgentResponse.SchemeInfo -> response.message
        is AgentResponse.Confirmation -> response.message
        is AgentResponse.Success -> response.message
        is AgentResponse.Error -> response.message
        is AgentResponse.Loading -> "Processing..."
    }

    private fun friendlyError(e: Exception): String = when {
        e.message?.contains("timeout", ignoreCase = true) == true ->
            "Your connection seems slow. Please try again."
        e.message?.contains("Unable to resolve", ignoreCase = true) == true ->
            "Cannot reach the banking server. Please check your connection."
        e.message?.contains("refused", ignoreCase = true) == true ->
            "Banking server is not responding. Please try later."
        else -> "I couldn't complete that request. Please try again."
    }

    override fun onCleared() {
        super.onCleared()
        audioRecorder.release()
        audioPlayer.release()
    }
}

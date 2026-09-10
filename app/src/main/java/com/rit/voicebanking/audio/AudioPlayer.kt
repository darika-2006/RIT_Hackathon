package com.rit.voicebanking.audio

import android.content.Context
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.speech.tts.TextToSpeech
import android.util.Log
import com.rit.voicebanking.domain.model.Language
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.Locale

/**
 * Manages TTS (Text-to-Speech) playback and remote audio URL playback.
 *
 * Priority:
 * 1. If backend provides a TTS audio URL, play that via MediaPlayer.
 * 2. Otherwise, use Android TTS engine as fallback.
 *
 * Lifecycle: Create per ViewModel, call [release] in onCleared.
 */
class AudioPlayer(private val context: Context) {

    enum class State { IDLE, PLAYING, ERROR }

    private val _state = MutableStateFlow(State.IDLE)
    val state: StateFlow<State> = _state.asStateFlow()

    private var mediaPlayer: MediaPlayer? = null
    private var tts: TextToSpeech? = null
    private var ttsReady = false

    init {
        initTts()
    }

    private fun initTts() {
        tts = TextToSpeech(context) { status ->
            ttsReady = (status == TextToSpeech.SUCCESS)
        }
    }

    /**
     * Play audio from a URL (e.g., backend TTS audio endpoint).
     */
    fun playFromUrl(url: String, onComplete: () -> Unit = {}) {
        stopPlayback()
        try {
            val player = MediaPlayer().apply {
                setAudioAttributes(
                    AudioAttributes.Builder()
                        .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                        .setUsage(AudioAttributes.USAGE_MEDIA)
                        .build()
                )
                setDataSource(url)
                setOnPreparedListener {
                    _state.value = State.PLAYING
                    start()
                }
                setOnCompletionListener {
                    _state.value = State.IDLE
                    onComplete()
                }
                setOnErrorListener { _, _, _ ->
                    _state.value = State.ERROR
                    true
                }
                prepareAsync()
            }
            mediaPlayer = player
        } catch (e: Exception) {
            Log.e("AudioPlayer", "playFromUrl failed", e)
            _state.value = State.ERROR
        }
    }

    /**
     * Speak text using Android TTS engine.
     * Used as fallback when backend doesn't provide audio URL.
     */
    fun speak(text: String, language: Language, onComplete: () -> Unit = {}) {
        if (!ttsReady) {
            onComplete()
            return
        }

        val locale = Locale.forLanguageTag(language.ttsLocale)
        val result = tts?.setLanguage(locale)
        if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
            tts?.setLanguage(Locale.ENGLISH)
        }

        tts?.setOnUtteranceProgressListener(object : android.speech.tts.UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) {
                _state.value = State.PLAYING
            }
            override fun onDone(utteranceId: String?) {
                _state.value = State.IDLE
                onComplete()
            }
            override fun onError(utteranceId: String?) {
                _state.value = State.ERROR
                onComplete()
            }
        })

        _state.value = State.PLAYING
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "vb_utterance")
    }

    fun stopPlayback() {
        try {
            mediaPlayer?.apply { if (isPlaying) stop(); release() }
        } catch (_: Exception) {}
        mediaPlayer = null
        tts?.stop()
        _state.value = State.IDLE
    }

    fun release() {
        stopPlayback()
        tts?.shutdown()
        tts = null
    }
}

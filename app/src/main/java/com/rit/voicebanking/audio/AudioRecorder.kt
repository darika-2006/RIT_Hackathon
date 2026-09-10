package com.rit.voicebanking.audio

import android.content.Context
import android.media.MediaRecorder
import android.os.Build
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.io.File

/**
 * Manages microphone recording.
 *
 * Produces a WAV/AAC file that the backend's ASR system will process.
 * If the backend requires a specific format (e.g. PCM 16kHz mono),
 * update [outputFormat] and [audioEncoder] accordingly.
 *
 * Lifecycle: Create once per screen/ViewModel, call [release] in onCleared.
 */
class AudioRecorder(private val context: Context) {

    enum class State { IDLE, RECORDING, ERROR }

    private val _state = MutableStateFlow(State.IDLE)
    val state: StateFlow<State> = _state.asStateFlow()

    private var recorder: MediaRecorder? = null
    private var outputFile: File? = null

    /**
     * Start recording.
     * @return The output file, or null if recording failed.
     */
    fun startRecording(): File? {
        return try {
            val file = createOutputFile()
            outputFile = file

            recorder = createMediaRecorder().apply {
                setAudioSource(MediaRecorder.AudioSource.MIC)
                setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
                setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
                setAudioSamplingRate(16000) // 16kHz — standard for ASR
                setAudioChannels(1)         // mono
                setOutputFile(file.absolutePath)
                prepare()
                start()
            }

            _state.value = State.RECORDING
            file
        } catch (e: Exception) {
            _state.value = State.ERROR
            release()
            null
        }
    }

    /**
     * Stop recording and return the recorded audio file.
     * Returns null if not currently recording.
     */
    fun stopRecording(): File? {
        return try {
            recorder?.apply {
                stop()
                release()
            }
            recorder = null
            _state.value = State.IDLE
            outputFile
        } catch (e: Exception) {
            _state.value = State.ERROR
            release()
            null
        }
    }

    /**
     * Cancel recording and discard any output.
     */
    fun cancelRecording() {
        try {
            recorder?.apply {
                stop()
                release()
            }
        } catch (_: Exception) {
            // Suppress — cancellation is best-effort
        } finally {
            recorder = null
            outputFile?.delete()
            outputFile = null
            _state.value = State.IDLE
        }
    }

    /**
     * Release all resources. Must be called when ViewModel is cleared.
     */
    fun release() {
        try {
            recorder?.release()
        } catch (_: Exception) {}
        recorder = null
        _state.value = State.IDLE
    }

    private fun createOutputFile(): File {
        val dir = context.cacheDir
        return File.createTempFile("voice_", ".m4a", dir)
    }

    @Suppress("DEPRECATION")
    private fun createMediaRecorder(): MediaRecorder =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            MediaRecorder(context)
        } else {
            MediaRecorder()
        }
}

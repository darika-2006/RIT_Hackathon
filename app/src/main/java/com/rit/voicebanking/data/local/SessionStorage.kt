package com.rit.voicebanking.data.local

import android.content.Context
import android.content.SharedPreferences

/**
 * Simple session storage using SharedPreferences.
 * Persists session ID and selected language across app restarts.
 */
class SessionStorage(context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences("voicebanking_session", Context.MODE_PRIVATE)

    var sessionId: String
        get() = prefs.getString(KEY_SESSION_ID, generateSessionId()) ?: generateSessionId()
        set(value) = prefs.edit().putString(KEY_SESSION_ID, value).apply()

    var languageCode: String
        get() = prefs.getString(KEY_LANGUAGE, "en") ?: "en"
        set(value) = prefs.edit().putString(KEY_LANGUAGE, value).apply()

    fun newSession(): String {
        val id = generateSessionId()
        sessionId = id
        return id
    }

    private fun generateSessionId(): String =
        "session_${System.currentTimeMillis()}"

    companion object {
        private const val KEY_SESSION_ID = "session_id"
        private const val KEY_LANGUAGE = "language_code"
    }
}

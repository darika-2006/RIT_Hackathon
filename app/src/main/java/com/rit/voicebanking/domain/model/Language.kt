package com.rit.voicebanking.domain.model

/**
 * Supported conversation languages.
 * The language code is sent to the backend; the backend returns responses in the same language.
 */
enum class Language(val code: String, val displayName: String, val ttsLocale: String) {
    ENGLISH("en", "English", "en-IN"),
    TAMIL("ta", "தமிழ்", "ta-IN"),
    HINDI("hi", "हिंदी", "hi-IN");

    companion object {
        fun fromCode(code: String): Language =
            entries.find { it.code == code } ?: ENGLISH
    }
}

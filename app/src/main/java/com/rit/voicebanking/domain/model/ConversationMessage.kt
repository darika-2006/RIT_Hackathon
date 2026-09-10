package com.rit.voicebanking.domain.model

/**
 * Represents a single turn in the conversation history.
 */
data class ConversationMessage(
    val id: String,
    val role: Role,
    val text: String,
    val timestamp: Long = System.currentTimeMillis(),
    val response: AgentResponse? = null  // rich card attached to assistant messages
)

enum class Role { USER, ASSISTANT }

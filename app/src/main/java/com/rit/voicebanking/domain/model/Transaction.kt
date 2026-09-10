package com.rit.voicebanking.domain.model

import java.time.LocalDateTime

/**
 * Domain model for a single banking transaction.
 * Populated entirely from backend response — never calculated on Android.
 */
data class Transaction(
    val id: String,
    val amount: Long,
    val currency: String = "INR",
    val type: TransactionType,
    val description: String,
    val merchant: String = "",
    val date: String, // ISO-8601 or human-readable from backend
    val status: TransactionStatus = TransactionStatus.COMPLETED
)

enum class TransactionType {
    CREDIT,  // money received
    DEBIT    // money spent
}

enum class TransactionStatus {
    COMPLETED,
    PENDING,
    FAILED,
    REVERSED
}

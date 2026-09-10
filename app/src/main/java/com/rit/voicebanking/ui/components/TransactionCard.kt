package com.rit.voicebanking.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowDownward
import androidx.compose.material.icons.filled.ArrowUpward
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.rit.voicebanking.domain.model.AgentResponse
import com.rit.voicebanking.domain.model.Transaction
import com.rit.voicebanking.domain.model.TransactionType
import com.rit.voicebanking.ui.theme.*

/**
 * Displays a list of transactions received from the backend.
 * Never fabricates transaction data.
 */
@Composable
fun TransactionListCard(
    transactions: AgentResponse.Transactions,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        shape = RoundedCornerShape(20.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "Recent Transactions",
                style = MaterialTheme.typography.headlineSmall,
                color = TextPrimary
            )

            if (transactions.transactions.isEmpty()) {
                Spacer(Modifier.height(12.dp))
                Text(
                    text = "No transactions found.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary
                )
            } else {
                Spacer(Modifier.height(8.dp))
                HorizontalDivider(color = SurfaceDim)
                transactions.transactions.forEach { tx ->
                    TransactionRow(tx)
                    HorizontalDivider(color = SurfaceDim)
                }
            }
        }
    }
}

@Composable
fun TransactionRow(transaction: Transaction) {
    val isCredit = transaction.type == TransactionType.CREDIT
    val amountColor = if (isCredit) CreditGreen else DebitRed
    val amountPrefix = if (isCredit) "+" else "-"

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Icon
        Box(
            modifier = Modifier
                .size(40.dp)
                .clip(CircleShape)
                .background(if (isCredit) SuccessGreen.copy(alpha = 0.12f) else ErrorRed.copy(alpha = 0.12f)),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = if (isCredit) Icons.Filled.ArrowDownward else Icons.Filled.ArrowUpward,
                contentDescription = if (isCredit) "Credit" else "Debit",
                tint = if (isCredit) CreditGreen else DebitRed,
                modifier = Modifier.size(20.dp)
            )
        }

        Spacer(Modifier.width(12.dp))

        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = transaction.description,
                style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.Medium),
                color = TextPrimary,
                maxLines = 1
            )
            Text(
                text = transaction.date,
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary
            )
        }

        Column(horizontalAlignment = Alignment.End) {
            Text(
                text = "$amountPrefix${formatCurrency(transaction.amount, transaction.currency)}",
                style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.Bold),
                color = amountColor
            )
            Text(
                text = transaction.status.name.lowercase().replaceFirstChar { it.uppercase() },
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary
            )
        }
    }
}

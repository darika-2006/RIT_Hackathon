package com.rit.voicebanking.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountBalance
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.rit.voicebanking.domain.model.AgentResponse
import com.rit.voicebanking.ui.theme.*

/**
 * Displays account balance — exactly as received from backend.
 * Never calculates or modifies the balance value.
 */
@Composable
fun BalanceCard(
    balance: AgentResponse.Balance,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        shape = RoundedCornerShape(20.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.linearGradient(
                        colors = listOf(BrandBlue, BrandBlueLight)
                    )
                )
                .padding(24.dp)
        ) {
            Column {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Icon(
                        Icons.Filled.AccountBalance,
                        contentDescription = null,
                        tint = TextOnBrand.copy(alpha = 0.8f),
                        modifier = Modifier.size(20.dp)
                    )
                    Text(
                        text = balance.accountType.uppercase(),
                        style = MaterialTheme.typography.labelLarge,
                        color = TextOnBrand.copy(alpha = 0.8f),
                        letterSpacing = 1.sp
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                Text(
                    text = "Available Balance",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextOnBrand.copy(alpha = 0.7f)
                )

                Spacer(modifier = Modifier.height(4.dp))

                Text(
                    text = formatCurrency(balance.balance, balance.currency),
                    style = MaterialTheme.typography.titleLarge.copy(
                        fontSize = 36.sp,
                        fontWeight = FontWeight.Bold,
                        color = TextOnBrand
                    )
                )

                if (balance.maskedAccountNumber.isNotBlank()) {
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        text = balance.maskedAccountNumber,
                        style = MaterialTheme.typography.bodySmall,
                        color = TextOnBrand.copy(alpha = 0.6f)
                    )
                }

                Spacer(modifier = Modifier.height(8.dp))

                Text(
                    text = "Updated just now",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextOnBrand.copy(alpha = 0.5f)
                )
            }
        }
    }
}

fun formatCurrency(amount: Long, currency: String = "INR"): String {
    val symbol = if (currency == "INR") "₹" else currency
    return "$symbol${"%,d".format(amount)}"
}

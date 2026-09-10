package com.rit.voicebanking.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.rit.voicebanking.domain.model.AgentResponse
import com.rit.voicebanking.ui.theme.*

/**
 * Confirmation card for sensitive banking operations.
 *
 * IMPORTANT: This card is shown ONLY when the backend sends requires_confirmation = true.
 * The frontend NEVER decides independently that confirmation is needed.
 */
@Composable
fun ConfirmationCard(
    confirmation: AgentResponse.Confirmation,
    onConfirm: () -> Unit,
    onCancel: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        shape = RoundedCornerShape(20.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceWhite)
    ) {
        Column(
            modifier = Modifier.padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                Icons.Filled.Warning,
                contentDescription = null,
                tint = WarningAmber,
                modifier = Modifier.size(40.dp)
            )

            Spacer(Modifier.height(12.dp))

            Text(
                text = "Confirm Request",
                style = MaterialTheme.typography.headlineSmall,
                color = TextPrimary,
                textAlign = TextAlign.Center
            )

            Spacer(Modifier.height(16.dp))

            // Action type
            Text(
                text = confirmation.action,
                style = MaterialTheme.typography.titleMedium.copy(
                    fontWeight = FontWeight.Bold,
                    fontSize = 18.sp
                ),
                color = BrandBlue
            )

            // Amount if present
            if (confirmation.amount != null) {
                Spacer(Modifier.height(8.dp))
                Text(
                    text = formatCurrency(confirmation.amount, confirmation.currency),
                    style = MaterialTheme.typography.titleLarge.copy(
                        fontSize = 32.sp,
                        fontWeight = FontWeight.ExtraBold
                    ),
                    color = TextMoney
                )
            }

            // Account type
            if (confirmation.accountType.isNotBlank()) {
                Spacer(Modifier.height(4.dp))
                Text(
                    text = "Into: ${confirmation.accountType}",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary
                )
            }

            Spacer(Modifier.height(16.dp))

            // Message from backend
            Text(
                text = confirmation.message,
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary,
                textAlign = TextAlign.Center
            )

            Spacer(Modifier.height(24.dp))

            Row(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                OutlinedButton(
                    onClick = onCancel,
                    modifier = Modifier
                        .weight(1f)
                        .height(52.dp),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text("Cancel", style = MaterialTheme.typography.labelLarge)
                }

                Button(
                    onClick = onConfirm,
                    modifier = Modifier
                        .weight(1f)
                        .height(52.dp),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = BrandBlue)
                ) {
                    Text("Confirm", style = MaterialTheme.typography.labelLarge, color = Color.White)
                }
            }
        }
    }
}

/**
 * Success card shown after a confirmed operation completes.
 */
@Composable
fun SuccessCard(
    success: AgentResponse.Success,
    onContinue: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        shape = RoundedCornerShape(20.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceWhite)
    ) {
        Column(
            modifier = Modifier.padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                Icons.Filled.CheckCircle,
                contentDescription = "Success",
                tint = SuccessGreen,
                modifier = Modifier.size(56.dp)
            )

            Spacer(Modifier.height(12.dp))

            Text(
                text = success.message,
                style = MaterialTheme.typography.bodyLarge.copy(fontWeight = FontWeight.Medium),
                color = TextPrimary,
                textAlign = TextAlign.Center
            )

            if (success.referenceId.isNotBlank()) {
                Spacer(Modifier.height(8.dp))
                Text(
                    text = "Ref: ${success.referenceId}",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary
                )
            }

            Spacer(Modifier.height(20.dp))

            Button(
                onClick = onContinue,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(containerColor = SuccessGreen)
            ) {
                Text("Done", style = MaterialTheme.typography.labelLarge, color = Color.White)
            }
        }
    }
}

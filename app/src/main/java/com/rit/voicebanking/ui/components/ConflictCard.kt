package com.rit.voicebanking.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ErrorOutline
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.rit.voicebanking.domain.model.AgentResponse
import com.rit.voicebanking.ui.theme.*

/**
 * Document conflict warning card.
 *
 * The backend detects the conflict (e.g. name mismatch between PAN and Aadhaar).
 * Android only renders the result — no fuzzy matching on the frontend.
 */
@Composable
fun ConflictCard(
    conflict: AgentResponse.Conflict,
    onReview: () -> Unit,
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
        Column(modifier = Modifier.padding(20.dp)) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(
                    Icons.Filled.ErrorOutline,
                    contentDescription = "Conflict",
                    tint = WarningAmber,
                    modifier = Modifier.size(28.dp)
                )
                Text(
                    text = "Information Mismatch",
                    style = MaterialTheme.typography.headlineSmall.copy(
                        fontWeight = FontWeight.Bold
                    ),
                    color = WarningAmber
                )
            }

            Spacer(Modifier.height(8.dp))

            Text(
                text = "Field: ${conflict.field}",
                style = MaterialTheme.typography.labelLarge,
                color = TextSecondary
            )

            Spacer(Modifier.height(16.dp))

            // Source A
            ConflictSourceRow(
                source = conflict.sourceA,
                value = conflict.valueA
            )

            Spacer(Modifier.height(8.dp))

            // VS divider
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Center
            ) {
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(4.dp))
                        .background(SurfaceDim)
                        .padding(horizontal = 12.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = "≠",
                        style = MaterialTheme.typography.labelLarge,
                        color = WarningAmber
                    )
                }
            }

            Spacer(Modifier.height(8.dp))

            // Source B
            ConflictSourceRow(
                source = conflict.sourceB,
                value = conflict.valueB
            )

            Spacer(Modifier.height(16.dp))

            Text(
                text = conflict.message.ifEmpty { "This difference may affect your application." },
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary,
                textAlign = TextAlign.Start
            )

            Spacer(Modifier.height(20.dp))

            Row(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                OutlinedButton(
                    onClick = onReview,
                    modifier = Modifier
                        .weight(1f)
                        .height(48.dp),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text("Review", style = MaterialTheme.typography.labelLarge)
                }

                Button(
                    onClick = onContinue,
                    modifier = Modifier
                        .weight(1f)
                        .height(48.dp),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = BrandBlue)
                ) {
                    Text("Continue", color = Color.White, style = MaterialTheme.typography.labelLarge)
                }
            }
        }
    }
}

@Composable
private fun ConflictSourceRow(source: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(SurfaceDim)
            .padding(horizontal = 14.dp, vertical = 10.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = source,
            style = MaterialTheme.typography.labelLarge,
            color = TextSecondary
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyLarge.copy(fontWeight = FontWeight.SemiBold),
            color = TextPrimary
        )
    }
}

package com.rit.voicebanking.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Assignment
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.rit.voicebanking.domain.model.AgentResponse
import com.rit.voicebanking.ui.theme.*

/**
 * Loan application progress card.
 *
 * Shows how many fields are already collected vs remaining.
 * Numbers come from backend — never hard-coded.
 */
@Composable
fun LoanProgressCard(
    loanProgress: AgentResponse.LoanProgress,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        shape = RoundedCornerShape(20.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(Icons.Filled.Assignment, contentDescription = null, tint = BrandBlue)
                Text(
                    text = loanProgress.loanType,
                    style = MaterialTheme.typography.headlineSmall,
                    color = TextPrimary
                )
            }

            Spacer(Modifier.height(4.dp))

            Text(
                text = "Application Progress",
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary
            )

            Spacer(Modifier.height(16.dp))

            // Progress bar
            val progress = if (loanProgress.totalFields > 0) {
                loanProgress.completedFields.toFloat() / loanProgress.totalFields.toFloat()
            } else 0f

            LinearProgressIndicator(
                progress = { progress },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp),
                color = BrandBlue,
                trackColor = SurfaceDim
            )

            Spacer(Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text(
                        text = "${loanProgress.completedFields}",
                        style = MaterialTheme.typography.titleLarge.copy(
                            fontWeight = FontWeight.Bold,
                            color = BrandBlue
                        )
                    )
                    Text(
                        text = "details collected",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary
                    )
                }

                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = "${loanProgress.remainingQuestions}",
                        style = MaterialTheme.typography.titleLarge.copy(
                            fontWeight = FontWeight.Bold,
                            color = AccentGold
                        )
                    )
                    Text(
                        text = "questions left",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary
                    )
                }
            }

            if (loanProgress.currentQuestion.isNotBlank()) {
                Spacer(Modifier.height(16.dp))
                HorizontalDivider(color = SurfaceDim)
                Spacer(Modifier.height(12.dp))

                if (loanProgress.remainingQuestions > 0) {
                    Text(
                        text = "Question ${loanProgress.currentQuestionIndex} of ${loanProgress.remainingQuestions}",
                        style = MaterialTheme.typography.labelMedium,
                        color = BrandBlue
                    )
                    Spacer(Modifier.height(4.dp))
                }

                Text(
                    text = loanProgress.currentQuestion,
                    style = MaterialTheme.typography.bodyLarge.copy(fontWeight = FontWeight.Medium),
                    color = TextPrimary
                )
            }
        }
    }
}

/**
 * Scheme information card for government loan schemes.
 */
@Composable
fun SchemeInfoCard(
    scheme: AgentResponse.SchemeInfo,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        shape = RoundedCornerShape(20.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Text(
                text = scheme.schemeName,
                style = MaterialTheme.typography.headlineSmall,
                color = BrandBlue
            )
            Spacer(Modifier.height(8.dp))
            Text(
                text = scheme.description,
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary
            )
            if (scheme.keyBenefits.isNotEmpty()) {
                Spacer(Modifier.height(12.dp))
                Text(
                    text = "Key Benefits",
                    style = MaterialTheme.typography.labelLarge,
                    color = TextPrimary
                )
                Spacer(Modifier.height(8.dp))
                scheme.keyBenefits.forEach { benefit ->
                    Row(
                        modifier = Modifier.padding(vertical = 2.dp),
                        verticalAlignment = Alignment.Top
                    ) {
                        Text("•  ", color = BrandBlue, style = MaterialTheme.typography.bodyMedium)
                        Text(
                            text = benefit,
                            style = MaterialTheme.typography.bodyMedium,
                            color = TextPrimary
                        )
                    }
                }
            }
        }
    }
}

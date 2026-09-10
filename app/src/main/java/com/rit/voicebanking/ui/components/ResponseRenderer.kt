package com.rit.voicebanking.ui.components

import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.rit.voicebanking.domain.model.AgentResponse
import com.rit.voicebanking.ui.theme.SurfaceWhite
import com.rit.voicebanking.ui.theme.TextPrimary

/**
 * Central response renderer.
 *
 * Inspects the concrete type of [AgentResponse] and delegates to the correct card component.
 * The conversation screen calls this once per assistant message — no switch statements in the UI.
 *
 * Adding a new response type only requires:
 *  1. Adding a new subtype to [AgentResponse]
 *  2. Adding a new branch here
 *  3. Creating the corresponding card Composable
 */
@Composable
fun ResponseRenderer(
    response: AgentResponse,
    onConfirm: () -> Unit = {},
    onCancel: () -> Unit = {},
    onConflictReview: () -> Unit = {},
    onConflictContinue: () -> Unit = {},
    onSuccessDone: () -> Unit = {},
    onRetry: () -> Unit = {},
    onSpeakAgain: () -> Unit = {},
    onGoHome: () -> Unit = {},
    modifier: Modifier = Modifier
) {
    when (response) {
        is AgentResponse.Balance ->
            BalanceCard(balance = response, modifier = modifier)

        is AgentResponse.Transactions ->
            TransactionListCard(transactions = response, modifier = modifier)

        is AgentResponse.TransactionDetail ->
            TransactionDetailCard(detail = response, modifier = modifier)

        is AgentResponse.Confirmation ->
            ConfirmationCard(
                confirmation = response,
                onConfirm = onConfirm,
                onCancel = onCancel,
                modifier = modifier
            )

        is AgentResponse.LoanProgress ->
            LoanProgressCard(loanProgress = response, modifier = modifier)

        is AgentResponse.LoanApplication ->
            LoanApplicationCard(application = response, modifier = modifier)

        is AgentResponse.Conflict ->
            ConflictCard(
                conflict = response,
                onReview = onConflictReview,
                onContinue = onConflictContinue,
                modifier = modifier
            )

        is AgentResponse.SchemeInfo ->
            SchemeInfoCard(scheme = response, modifier = modifier)

        is AgentResponse.Success ->
            SuccessCard(
                success = response,
                onContinue = onSuccessDone,
                modifier = modifier
            )

        is AgentResponse.Error ->
            ErrorCard(
                message = response.message,
                retryable = response.retryable,
                onRetry = onRetry,
                onSpeakAgain = onSpeakAgain,
                onGoHome = onGoHome,
                modifier = modifier
            )

        is AgentResponse.Text ->
            TextResponseCard(text = response.message, modifier = modifier)

        is AgentResponse.Loading ->
            LoadingCard("Processing your request...", modifier = modifier)
    }
}

/**
 * Simple text bubble card for plain conversational responses.
 */
@Composable
fun TextResponseCard(text: String, modifier: Modifier = Modifier) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 4.dp),
        shape = RoundedCornerShape(16.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceWhite)
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.bodyLarge,
            color = TextPrimary,
            modifier = Modifier.padding(16.dp)
        )
    }
}

/**
 * Loan application summary card.
 */
@Composable
fun LoanApplicationCard(
    application: AgentResponse.LoanApplication,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        shape = RoundedCornerShape(20.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        androidx.compose.foundation.layout.Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = androidx.compose.foundation.layout.Arrangement.spacedBy(6.dp)
        ) {
            Text(
                text = application.schemeName,
                style = MaterialTheme.typography.headlineSmall,
                color = com.rit.voicebanking.ui.theme.BrandBlue
            )
            if (application.maxAmount > 0) {
                Text(
                    text = "Max Loan: ${formatCurrency(application.maxAmount)}",
                    style = MaterialTheme.typography.bodyLarge,
                    color = TextPrimary
                )
            }
            if (application.interestRate.isNotBlank()) {
                Text(
                    text = "Interest Rate: ${application.interestRate}",
                    style = MaterialTheme.typography.bodyMedium,
                    color = com.rit.voicebanking.ui.theme.TextSecondary
                )
            }
            if (application.tenure.isNotBlank()) {
                Text(
                    text = "Tenure: ${application.tenure}",
                    style = MaterialTheme.typography.bodyMedium,
                    color = com.rit.voicebanking.ui.theme.TextSecondary
                )
            }
            if (application.eligibility.isNotBlank()) {
                Text(
                    text = application.eligibility,
                    style = MaterialTheme.typography.bodySmall,
                    color = com.rit.voicebanking.ui.theme.TextSecondary
                )
            }
        }
    }
}

/**
 * Single transaction detail card.
 */
@Composable
fun TransactionDetailCard(
    detail: AgentResponse.TransactionDetail,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        shape = RoundedCornerShape(20.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        androidx.compose.foundation.layout.Column(modifier = Modifier.padding(20.dp)) {
            val tx = detail.transaction
            Text(
                text = tx.description,
                style = MaterialTheme.typography.headlineSmall,
                color = TextPrimary
            )
            androidx.compose.foundation.layout.Spacer(Modifier.padding(4.dp))
            TransactionRow(transaction = tx)
        }
    }
}

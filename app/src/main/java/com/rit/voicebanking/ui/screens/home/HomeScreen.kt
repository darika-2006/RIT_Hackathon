package com.rit.voicebanking.ui.screens.home

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.rit.voicebanking.BuildConfig
import com.rit.voicebanking.R
import com.rit.voicebanking.domain.model.Language
import com.rit.voicebanking.ui.components.MicrophoneButton
import com.rit.voicebanking.ui.screens.conversation.ConversationUiState
import com.rit.voicebanking.ui.screens.conversation.ConversationViewModel
import com.rit.voicebanking.ui.theme.*

/**
 * Home / Voice Dashboard screen.
 *
 * The microphone is visually dominant.
 * Quick actions are secondary fallbacks for users who prefer tapping.
 */
@Composable
fun HomeScreen(
    viewModel: ConversationViewModel,
    onNavigateToConversation: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()
    val language by viewModel.selectedLanguage.collectAsState()

    val isRecording = uiState is ConversationUiState.Recording
    val isProcessing = uiState is ConversationUiState.Processing ||
            uiState is ConversationUiState.Uploading

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(SurfaceLight)
    ) {
        // ── Top bar ─────────────────────────────────────────────────────────
        HomeTopBar(language = language)

        // ── Center: mic + status ──────────────────────────────────────────
        Column(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = stringResource(R.string.home_prompt),
                style = MaterialTheme.typography.headlineMedium.copy(
                    fontWeight = FontWeight.Normal,
                    color = TextSecondary
                ),
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(horizontal = 32.dp)
            )

            Spacer(Modifier.height(40.dp))

            MicrophoneButton(
                isRecording = isRecording,
                isProcessing = isProcessing,
                onClick = {
                    when {
                        isRecording -> {
                            viewModel.stopRecordingAndSend()
                            onNavigateToConversation()
                        }
                        isProcessing -> { /* do nothing while processing */ }
                        else -> {
                            viewModel.startListening()
                        }
                    }
                },
                size = 96.dp
            )

            Spacer(Modifier.height(24.dp))

            // Status text
            val statusText = when {
                isRecording -> stringResource(R.string.status_recording)
                isProcessing -> stringResource(R.string.status_processing)
                else -> stringResource(R.string.status_tap_speak)
            }

            Text(
                text = statusText,
                style = MaterialTheme.typography.bodyLarge,
                color = if (isRecording) MicListening else TextSecondary
            )

            if (isRecording) {
                Spacer(Modifier.height(16.dp))
                OutlinedButton(
                    onClick = { viewModel.cancelRecording() },
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text(stringResource(R.string.cancel))
                }
            }

            if (BuildConfig.DEMO_MODE) {
                Spacer(Modifier.height(8.dp))
                DemoBadge()
            }
        }

        // ── Quick actions ────────────────────────────────────────────────
        QuickActionsRow(
            onAction = { text ->
                viewModel.sendQuickAction(text)
                onNavigateToConversation()
            }
        )

        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun HomeTopBar(language: Language) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                Brush.horizontalGradient(listOf(BrandBlueDark, BrandBlue))
            )
            .padding(horizontal = 20.dp, vertical = 16.dp)
    ) {
        Column {
            Text(
                text = "Good day! 👋",
                style = MaterialTheme.typography.bodyMedium,
                color = Color.White.copy(alpha = 0.8f)
            )
            Text(
                text = "Your Banking Assistant",
                style = MaterialTheme.typography.headlineMedium.copy(
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
            )
        }

        // Language indicator (top right)
        Box(
            modifier = Modifier
                .align(Alignment.CenterEnd)
                .clip(RoundedCornerShape(8.dp))
                .background(Color.White.copy(alpha = 0.2f))
                .padding(horizontal = 10.dp, vertical = 6.dp)
        ) {
            Text(
                text = language.displayName,
                style = MaterialTheme.typography.labelLarge,
                color = Color.White
            )
        }
    }
}

@Composable
private fun QuickActionsRow(onAction: (String) -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp)
    ) {
        Text(
            text = "Quick Actions",
            style = MaterialTheme.typography.labelLarge,
            color = TextSecondary,
            modifier = Modifier.padding(bottom = 8.dp)
        )
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            QuickActionChip(
                icon = Icons.Filled.AccountBalance,
                label = "Balance",
                onClick = { onAction("What is my balance?") },
                modifier = Modifier.weight(1f)
            )
            QuickActionChip(
                icon = Icons.Filled.Receipt,
                label = "Transactions",
                onClick = { onAction("Show my recent transactions") },
                modifier = Modifier.weight(1f)
            )
            QuickActionChip(
                icon = Icons.Filled.AttachMoney,
                label = "Loans",
                onClick = { onAction("I want to apply for a Mudra loan") },
                modifier = Modifier.weight(1f)
            )
            QuickActionChip(
                icon = Icons.Filled.Savings,
                label = "Deposit",
                onClick = { onAction("I want to make a deposit") },
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
private fun QuickActionChip(
    icon: ImageVector,
    label: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    ElevatedCard(
        onClick = onClick,
        modifier = modifier,
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.elevatedCardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(10.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Icon(icon, contentDescription = label, tint = BrandBlue, modifier = Modifier.size(22.dp))
            Text(
                text = label,
                style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Medium),
                color = TextPrimary,
                textAlign = TextAlign.Center,
                maxLines = 1
            )
        }
    }
}

@Composable
private fun DemoBadge() {
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(6.dp))
            .background(AccentGold.copy(alpha = 0.2f))
            .padding(horizontal = 10.dp, vertical = 4.dp)
    ) {
        Text(
            text = "DEMO MODE",
            style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold),
            color = AccentGold
        )
    }
}

@Preview
@Composable
fun HomeScreenPreview() {
    // Preview not functional without ViewModel
}

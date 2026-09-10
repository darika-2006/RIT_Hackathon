package com.rit.voicebanking.ui.screens.conversation

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.rit.voicebanking.domain.model.ConversationMessage
import com.rit.voicebanking.domain.model.Role
import com.rit.voicebanking.ui.components.*
import com.rit.voicebanking.ui.theme.*

/**
 * Conversation screen — the main interaction screen after the user starts speaking.
 *
 * Shows:
 * - Chat history (user + assistant messages)
 * - Rich response cards inline with chat
 * - State-driven overlays (processing, listening, confirmation, error)
 * - Microphone button + text input
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ConversationScreen(
    viewModel: ConversationViewModel,
    onNavigateBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()
    val messages by viewModel.messages.collectAsState()
    val listState = rememberLazyListState()

    var textInput by remember { mutableStateOf("") }

    val isRecording = uiState is ConversationUiState.Recording
    val isProcessing = uiState is ConversationUiState.Processing ||
            uiState is ConversationUiState.Uploading

    // Auto-scroll to newest message
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.size - 1)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        "Banking Assistant",
                        style = MaterialTheme.typography.titleMedium
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.replayTts() }) {
                        Icon(Icons.Filled.VolumeUp, "Replay response")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = BrandBlue,
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White,
                    actionIconContentColor = Color.White
                )
            )
        },
        bottomBar = {
            ConversationInputBar(
                textInput = textInput,
                onTextChange = { textInput = it },
                isRecording = isRecording,
                isProcessing = isProcessing,
                onSendText = {
                    if (textInput.isNotBlank()) {
                        viewModel.sendText(textInput)
                        textInput = ""
                    }
                },
                onMicClick = {
                    if (isRecording) {
                        viewModel.stopRecordingAndSend()
                    } else if (!isProcessing) {
                        viewModel.startListening()
                    }
                },
                onCancelRecording = { viewModel.cancelRecording() }
            )
        },
        containerColor = SurfaceLight
    ) { padding ->
        LazyColumn(
            state = listState,
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentPadding = PaddingValues(vertical = 8.dp)
        ) {
            // Empty state
            if (messages.isEmpty()) {
                item {
                    EmptyConversationState()
                }
            }

            items(messages, key = { it.id }) { message ->
                ConversationMessageItem(
                    message = message,
                    onConfirm = { viewModel.confirmAction() },
                    onCancel = { viewModel.cancelAction() },
                    onConflictReview = { /* no-op: can add document review screen */ },
                    onConflictContinue = { viewModel.sendText("Continue with application") },
                    onSuccessDone = { viewModel.goHome() },
                    onRetry = { viewModel.retry() },
                    onSpeakAgain = { viewModel.startListening() },
                    onGoHome = { viewModel.goHome() }
                )
            }

            // In-line state cards
            when (val state = uiState) {
                is ConversationUiState.Listening ->
                    item { LoadingCard("Listening...", modifier = Modifier.padding(horizontal = 16.dp)) }

                is ConversationUiState.Uploading ->
                    item { LoadingCard("Sending audio...", modifier = Modifier.padding(horizontal = 16.dp)) }

                is ConversationUiState.Processing ->
                    item { ProcessingStepsCard() }

                is ConversationUiState.Error -> {
                    // Error already added as message if it's a backend error
                    // Show inline error card if not already in messages
                    item {
                        ErrorCard(
                            message = state.message,
                            retryable = state.retryable,
                            onRetry = { viewModel.retry() },
                            onSpeakAgain = { viewModel.startListening() },
                            onGoHome = { viewModel.goHome() }
                        )
                    }
                }

                else -> {}
            }
        }
    }
}

@Composable
private fun ConversationMessageItem(
    message: ConversationMessage,
    onConfirm: () -> Unit,
    onCancel: () -> Unit,
    onConflictReview: () -> Unit,
    onConflictContinue: () -> Unit,
    onSuccessDone: () -> Unit,
    onRetry: () -> Unit,
    onSpeakAgain: () -> Unit,
    onGoHome: () -> Unit
) {
    Column(modifier = Modifier.fillMaxWidth()) {
        when (message.role) {
            Role.USER -> UserMessageBubble(text = message.text)
            Role.ASSISTANT -> {
                AssistantMessageBubble(text = message.text)
                // Show rich card if available
                message.response?.let { response ->
                    ResponseRenderer(
                        response = response,
                        onConfirm = onConfirm,
                        onCancel = onCancel,
                        onConflictReview = onConflictReview,
                        onConflictContinue = onConflictContinue,
                        onSuccessDone = onSuccessDone,
                        onRetry = onRetry,
                        onSpeakAgain = onSpeakAgain,
                        onGoHome = onGoHome
                    )
                }
            }
        }
    }
}

@Composable
private fun UserMessageBubble(text: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 4.dp),
        horizontalArrangement = Arrangement.End
    ) {
        Box(
            modifier = Modifier
                .widthIn(max = 280.dp)
                .clip(
                    RoundedCornerShape(
                        topStart = 18.dp, topEnd = 18.dp,
                        bottomStart = 18.dp, bottomEnd = 4.dp
                    )
                )
                .background(UserBubble)
                .padding(horizontal = 16.dp, vertical = 10.dp)
        ) {
            Text(
                text = text,
                style = MaterialTheme.typography.bodyLarge,
                color = UserBubbleText
            )
        }
    }
}

@Composable
private fun AssistantMessageBubble(text: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 4.dp),
        horizontalArrangement = Arrangement.Start,
        verticalAlignment = Alignment.Top
    ) {
        // Assistant avatar
        Box(
            modifier = Modifier
                .size(32.dp)
                .clip(CircleShape)
                .background(BrandBlue),
            contentAlignment = Alignment.Center
        ) {
            Text("A", style = MaterialTheme.typography.labelLarge, color = Color.White)
        }

        Spacer(Modifier.width(8.dp))

        Box(
            modifier = Modifier
                .widthIn(max = 280.dp)
                .clip(
                    RoundedCornerShape(
                        topStart = 4.dp, topEnd = 18.dp,
                        bottomStart = 18.dp, bottomEnd = 18.dp
                    )
                )
                .background(AssistantBubble)
                .padding(horizontal = 16.dp, vertical = 10.dp)
        ) {
            Text(
                text = text,
                style = MaterialTheme.typography.bodyLarge,
                color = AssistantBubbleText
            )
        }
    }
}

@Composable
private fun ProcessingStepsCard() {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceWhite)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            ProcessingStep("Voice received", done = true)
            ProcessingStep("Understanding request", done = true)
            ProcessingStep("Checking your account...", done = false, inProgress = true)
        }
    }
}

@Composable
private fun ProcessingStep(text: String, done: Boolean, inProgress: Boolean = false) {
    Row(
        modifier = Modifier.padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        if (done) {
            Text("✓", color = SuccessGreen, style = MaterialTheme.typography.bodyMedium)
        } else if (inProgress) {
            CircularProgressIndicator(
                modifier = Modifier.size(14.dp),
                color = BrandBlue,
                strokeWidth = 2.dp
            )
        } else {
            Text("•", color = TextHint, style = MaterialTheme.typography.bodyMedium)
        }
        Text(
            text = text,
            style = MaterialTheme.typography.bodyMedium,
            color = if (done) TextSecondary else TextPrimary
        )
    }
}

@Composable
private fun EmptyConversationState() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Text("👋", style = MaterialTheme.typography.displayLarge)
        Text(
            "Tap the microphone to speak",
            style = MaterialTheme.typography.bodyLarge,
            color = TextSecondary,
            textAlign = TextAlign.Center
        )
        Text(
            "or type your question below",
            style = MaterialTheme.typography.bodyMedium,
            color = TextHint,
            textAlign = TextAlign.Center
        )
    }
}

@Composable
private fun ConversationInputBar(
    textInput: String,
    onTextChange: (String) -> Unit,
    isRecording: Boolean,
    isProcessing: Boolean,
    onSendText: () -> Unit,
    onMicClick: () -> Unit,
    onCancelRecording: () -> Unit
) {
    Surface(
        shadowElevation = 8.dp,
        color = SurfaceWhite
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 8.dp)
                .navigationBarsPadding(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            if (isRecording) {
                // Cancel button visible during recording
                OutlinedButton(
                    onClick = onCancelRecording,
                    modifier = Modifier.height(48.dp)
                ) {
                    Text("Cancel")
                }
                Spacer(Modifier.weight(1f))
                Text(
                    "Recording...",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MicListening
                )
            } else {
                // Text field
                OutlinedTextField(
                    value = textInput,
                    onValueChange = onTextChange,
                    modifier = Modifier.weight(1f),
                    placeholder = {
                        Text("Type your question...", color = TextHint)
                    },
                    singleLine = true,
                    shape = RoundedCornerShape(24.dp),
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                    keyboardActions = KeyboardActions(onSend = { onSendText() }),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = BrandBlue,
                        unfocusedBorderColor = TextHint
                    )
                )

                // Send text button (only if text entered)
                if (textInput.isNotBlank()) {
                    IconButton(
                        onClick = onSendText,
                        modifier = Modifier
                            .size(48.dp)
                            .clip(CircleShape)
                            .background(BrandBlue)
                    ) {
                        Icon(
                            Icons.AutoMirrored.Filled.Send,
                            contentDescription = "Send",
                            tint = Color.White
                        )
                    }
                }
            }

            // Microphone button
            MicrophoneButton(
                isRecording = isRecording,
                isProcessing = isProcessing,
                onClick = onMicClick,
                size = 52.dp
            )
        }
    }
}

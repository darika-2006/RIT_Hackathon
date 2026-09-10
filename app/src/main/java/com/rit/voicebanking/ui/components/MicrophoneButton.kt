package com.rit.voicebanking.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.rit.voicebanking.ui.theme.*

/**
 * The primary microphone button — the dominant UI element on the home and conversation screens.
 *
 * States:
 *  - Idle:       large blue mic, tap to record
 *  - Recording:  pulsing red mic + stop icon
 *  - Processing: circular progress indicator
 */
@Composable
fun MicrophoneButton(
    isRecording: Boolean,
    isProcessing: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    size: Dp = 88.dp
) {
    val buttonColor = when {
        isRecording -> MicListening
        isProcessing -> MicProcessing
        else -> MicIdle
    }

    // Pulse animation when recording
    val infiniteTransition = rememberInfiniteTransition(label = "mic_pulse")
    val scale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = if (isRecording) 1.12f else 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(800, easing = EaseInOut),
            repeatMode = RepeatMode.Reverse
        ),
        label = "mic_scale"
    )

    Box(
        modifier = modifier,
        contentAlignment = Alignment.Center
    ) {
        // Outer glow ring (only when recording)
        if (isRecording) {
            Box(
                modifier = Modifier
                    .size(size + 24.dp)
                    .scale(scale)
                    .background(MicListening.copy(alpha = 0.15f), CircleShape)
            )
        }

        if (isProcessing) {
            CircularProgressIndicator(
                modifier = Modifier.size(size + 8.dp),
                color = BrandBlue,
                strokeWidth = 3.dp
            )
        }

        FilledIconButton(
            onClick = onClick,
            modifier = Modifier
                .size(size)
                .scale(if (isRecording) scale else 1f),
            colors = IconButtonDefaults.filledIconButtonColors(
                containerColor = buttonColor,
                contentColor = Color.White
            )
        ) {
            Icon(
                imageVector = if (isRecording) Icons.Filled.Stop else Icons.Filled.Mic,
                contentDescription = if (isRecording) "Stop recording" else "Start recording",
                modifier = Modifier.size(size * 0.42f)
            )
        }
    }
}

package com.rit.voicebanking.ui.theme

import android.app.Activity
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val VoiceBankingColorScheme = lightColorScheme(
    primary = BrandBlue,
    onPrimary = TextOnBrand,
    primaryContainer = SurfaceDim,
    onPrimaryContainer = BrandBlueDark,
    secondary = AccentGold,
    onSecondary = TextPrimary,
    secondaryContainer = Color(0xFFFFF8E1),
    onSecondaryContainer = TextPrimary,
    tertiary = SuccessGreen,
    onTertiary = Color.White,
    background = SurfaceLight,
    onBackground = TextPrimary,
    surface = SurfaceWhite,
    onSurface = TextPrimary,
    surfaceVariant = SurfaceDim,
    onSurfaceVariant = TextSecondary,
    error = ErrorRed,
    onError = Color.White,
    outline = TextHint
)

@Composable
fun VoiceBankingTheme(
    content: @Composable () -> Unit
) {
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = BrandBlue.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = false
        }
    }

    MaterialTheme(
        colorScheme = VoiceBankingColorScheme,
        typography = VoiceBankingTypography,
        content = content
    )
}

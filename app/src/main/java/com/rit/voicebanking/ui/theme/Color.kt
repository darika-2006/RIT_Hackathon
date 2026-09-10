package com.rit.voicebanking.ui.theme

import androidx.compose.ui.graphics.Color

// ─── Brand Colors ─────────────────────────────────────────────────────────────
// Deep trustworthy blue — primary brand color
val BrandBlue = Color(0xFF1A3A6B)
val BrandBlueDark = Color(0xFF0F2547)
val BrandBlueLight = Color(0xFF2657A8)

// Accent — gold/amber for important values (balances, amounts)
val AccentGold = Color(0xFFD4A017)
val AccentGoldLight = Color(0xFFF5C842)

// Success green
val SuccessGreen = Color(0xFF2E7D32)
val SuccessGreenLight = Color(0xFF43A047)

// Error/warning red
val ErrorRed = Color(0xFFC62828)
val ErrorRedLight = Color(0xFFEF5350)

// Warning amber
val WarningAmber = Color(0xFFE65100)
val WarningAmberLight = Color(0xFFFF8F00)

// ─── Surface Colors ───────────────────────────────────────────────────────────
val SurfaceWhite = Color(0xFFFFFFFF)
val SurfaceLight = Color(0xFFF5F7FA)
val SurfaceCard = Color(0xFFFFFFFF)
val SurfaceDim = Color(0xFFEEF2F8)

// ─── Text Colors ──────────────────────────────────────────────────────────────
val TextPrimary = Color(0xFF1A1A2E)
val TextSecondary = Color(0xFF5C6B8A)
val TextHint = Color(0xFF9AA5BB)
val TextOnBrand = Color(0xFFFFFFFF)
val TextMoney = Color(0xFF1A3A6B)

// ─── Microphone ──────────────────────────────────────────────────────────────
val MicIdle = BrandBlue
val MicListening = Color(0xFFE53935)    // red — recording in progress
val MicProcessing = Color(0xFF1565C0)   // blue-processing

// ─── Transaction colors ───────────────────────────────────────────────────────
val CreditGreen = Color(0xFF2E7D32)
val DebitRed = Color(0xFFC62828)

// ─── Chat bubble colors ───────────────────────────────────────────────────────
val UserBubble = BrandBlue
val UserBubbleText = Color(0xFFFFFFFF)
val AssistantBubble = Color(0xFFEEF2F8)
val AssistantBubbleText = TextPrimary

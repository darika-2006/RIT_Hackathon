package com.rit.voicebanking

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.core.content.ContextCompat
import com.rit.voicebanking.ui.navigation.AppNavGraph
import com.rit.voicebanking.ui.theme.SurfaceLight
import com.rit.voicebanking.ui.theme.VoiceBankingTheme

/**
 * Single Activity host.
 *
 * Responsibilities:
 * - Request RECORD_AUDIO permission on launch
 * - Set up the Compose content with VoiceBankingTheme
 * - Host the NavHost
 *
 * No business logic lives here.
 */
class MainActivity : ComponentActivity() {

    private val requestMicPermission = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (!granted) {
            Toast.makeText(
                this,
                "Microphone permission is needed for voice input. You can still use text input.",
                Toast.LENGTH_LONG
            ).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        // Request microphone permission proactively
        requestMicPermissionIfNeeded()

        setContent {
            VoiceBankingTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = SurfaceLight
                ) {
                    AppNavGraph(application = application)
                }
            }
        }
    }

    private fun requestMicPermissionIfNeeded() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
            != PackageManager.PERMISSION_GRANTED
        ) {
            requestMicPermission.launch(Manifest.permission.RECORD_AUDIO)
        }
    }
}

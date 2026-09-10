package com.rit.voicebanking.ui.screens.conversation

import android.app.Application
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.rit.voicebanking.BuildConfig
import com.rit.voicebanking.data.remote.NetworkClient
import com.rit.voicebanking.data.repository.DemoBankingRepository
import com.rit.voicebanking.data.repository.RemoteBankingRepository
import com.rit.voicebanking.domain.repository.BankingRepository

/**
 * ViewModelFactory that selects the correct BankingRepository implementation.
 *
 * DEMO MODE:   BuildConfig.DEMO_MODE = true  → DemoBankingRepository
 * PRODUCTION:  BuildConfig.DEMO_MODE = false → RemoteBankingRepository
 *
 * To switch from demo to production, change DEMO_MODE in app/build.gradle.kts.
 * To use production mode with a specific URL, also update BASE_URL there.
 */
class ConversationViewModelFactory(
    private val application: Application,
    private val forceDemoMode: Boolean = BuildConfig.DEMO_MODE
) : ViewModelProvider.Factory {

    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (!modelClass.isAssignableFrom(ConversationViewModel::class.java)) {
            throw IllegalArgumentException("Unknown ViewModel: ${modelClass.name}")
        }

        val repository: BankingRepository = if (forceDemoMode) {
            DemoBankingRepository()
        } else {
            RemoteBankingRepository(NetworkClient.apiService)
        }

        @Suppress("UNCHECKED_CAST")
        return ConversationViewModel(application, repository) as T
    }
}

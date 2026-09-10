package com.rit.voicebanking.ui.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.rit.voicebanking.domain.model.Language
import com.rit.voicebanking.ui.screens.conversation.ConversationScreen
import com.rit.voicebanking.ui.screens.conversation.ConversationViewModel
import com.rit.voicebanking.ui.screens.conversation.ConversationViewModelFactory
import com.rit.voicebanking.ui.screens.home.HomeScreen
import com.rit.voicebanking.ui.screens.welcome.WelcomeScreen

object Routes {
    const val WELCOME = "welcome"
    const val HOME = "home"
    const val CONVERSATION = "conversation"
}

@Composable
fun AppNavGraph(
    application: android.app.Application,
    navController: NavHostController = rememberNavController()
) {
    val viewModel: ConversationViewModel = viewModel(
        factory = ConversationViewModelFactory(application)
    )

    NavHost(
        navController = navController,
        startDestination = Routes.WELCOME
    ) {
        composable(Routes.WELCOME) {
            WelcomeScreen(
                onStartTalking = { language ->
                    viewModel.setLanguage(language)
                    navController.navigate(Routes.HOME)
                }
            )
        }

        composable(Routes.HOME) {
            HomeScreen(
                viewModel = viewModel,
                onNavigateToConversation = {
                    navController.navigate(Routes.CONVERSATION)
                }
            )
        }

        composable(Routes.CONVERSATION) {
            ConversationScreen(
                viewModel = viewModel,
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
    }
}

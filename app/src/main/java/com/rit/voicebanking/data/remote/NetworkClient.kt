package com.rit.voicebanking.data.remote

import com.rit.voicebanking.BuildConfig
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Singleton Retrofit/OkHttp setup.
 *
 * ──────────────────────────────────────────────
 * CONFIGURATION
 * To change the backend URL, update build.gradle.kts:
 *   buildConfigField("String", "BASE_URL", "\"http://YOUR_IP:PORT/\"")
 *
 * Emulator → host localhost:   http://10.0.2.2:8000/
 * Physical device (same WiFi): http://192.168.x.x:8000/
 * ──────────────────────────────────────────────
 */
object NetworkClient {

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = if (BuildConfig.DEBUG) {
            HttpLoggingInterceptor.Level.BODY
        } else {
            HttpLoggingInterceptor.Level.NONE
        }
    }

    private val okHttpClient: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    val apiService: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }

    val asrApiService: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BuildConfig.ASR_BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}

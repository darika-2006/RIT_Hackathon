# Add project specific ProGuard rules here.
# By default, the flags in this file are appended to flags specified
# in /SDK/tools/proguard/proguard-android.txt

# Retrofit
-keepattributes Signature
-keepattributes *Annotation*
-keep class retrofit2.** { *; }
-keep interface retrofit2.** { *; }

# Gson
-keep class com.google.gson.** { *; }
-keep class com.rit.voicebanking.data.remote.** { *; }

# Keep domain models
-keep class com.rit.voicebanking.domain.model.** { *; }

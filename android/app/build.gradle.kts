plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "com.example.vocab_11"
    compileSdk = 37
    ndkVersion = "28.2.13676358" // Required for native C++ channels in speech plugins

    defaultConfig {
        applicationId = "com.example.vocab_11"
        minSdk = 26             // Required for Hive binary caches & SQLite services
        targetSdk = 37
        versionCode = 1
        versionName = "1.0.0"
        multiDexEnabled = true   // Prevents the 64k method limit crash on debug builds
    }

    buildTypes {
        getByName("release") {
            signingConfig = signingConfigs.getByName("debug")
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
        isCoreLibraryDesugaringEnabled = true // Backports Java 8 time libraries to older phones
    }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

dependencies {
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")
    // Enforce matching, stable Firebase SDK versions using the BOM platform
    implementation(platform("com.google.firebase:firebase-bom:33.5.0"))
    
    // Align the messaging package with the rules specified by the BOM above
    implementation("com.google.firebase:firebase-messaging")
}

configurations.all {
    resolutionStrategy.eachDependency {
        if (requested.group == "com.google.firebase" && requested.name == "firebase-iid") {
            useVersion("21.1.0")
        }
    }
}



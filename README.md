# ComicCraft Android

Android-native version of the supplied ComicCraft FastAPI project.

## Build on GitHub (recommended for phone users)
1. Upload the project root to a GitHub repository.
2. Open **Actions**.
3. Select **Build ComicCraft APK**.
4. Choose **Run workflow**.
5. Download the `ComicCraft-debug-apk` artifact and install `app-debug.apk` on Android.

The repository contains Gradle wrapper configuration and `gradlew` launch scripts. The GitHub Actions workflow installs Gradle 8.10 directly so the APK build works even if the wrapper JAR has not been generated on the phone.

## API keys
The app asks for Gemini and Hugging Face keys at runtime and stores them in Android app preferences. Do not hard-code production secrets into the APK.

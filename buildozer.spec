[app]
title = Echo Boarding School
package.name = echoboardingschool
package.domain = org.example
source.dir = .
source.include_exts = py,ttf
version = 0.1
requirements = python3,pygame
orientation = landscape
fullscreen = 1
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.gradle_dependencies = 'org.libsdl.app:SDL2:2.0.12'
[buildozer]
log_level = 2
warn_on_root = 1
android.accept_sdk_license = True

# Use system Android SDK
android.sdk_path = /home/runner/android-sdk
android.ndk_path = /home/runner/.buildozer/android/platform/android-ndk
android.entrypoint = org.kivy.android.PythonActivity
android.skip_update = True

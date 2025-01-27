OneLink Generator
A Python package for generating platform-specific URLs for Android and iOS with support for custom parameters and fallback URLs.

Installation
You can install the package via pip from PyPI:

pip install onelink
Or, if you're testing the package from the local source or TestPyPI, use:

pip install --index-url https://test.pypi.org/simple/ onelink
Usage
1. Basic Setup
To generate OneLink-style URLs for Android and iOS, you need to set the App IDs for each platform and any other parameters you want to include.

2. Creating a Custom Link
from onelink.generator import AppLinkGenerator

# Initialize the generator with your custom domain
gen = AppLinkGenerator(base_url="https://yourdomain.com")

# Set the Android and iOS App IDs
gen.set_android_app_id("com.example.android")
gen.set_ios_app_id("123456789")

# Optionally, set fallback URLs (for when the app is not installed)
gen.set_android_fallback_url("https://play.google.com/store/apps/details?id=com.example.android")
gen.set_ios_fallback_url("https://apps.apple.com/us/app/example/id123456789")

# Add custom UTM parameters or any other tracking info
gen.set_custom_param("utm_source", "email", platform="android")
gen.set_custom_param("utm_campaign", "holiday2025", platform="ios")

# Generate platform-specific links
android_link = gen.generate_android_link()
ios_link = gen.generate_ios_link()

# Output the generated links
print("Android Link:", android_link)
print("iOS Link:", ios_link)
Generated Links
Android Link: https://yourdomain.com/android?app_id=com.example.android&utm_source=email&utm_campaign=holiday2025&fallback_url=https://play.google.com/store/apps/details?id=com.example.android
iOS Link: https://yourdomain.com/ios?app_id=123456789&utm_campaign=holiday2025&fallback_url=https://apps.apple.com/us/app/example/id123456789&utm_source=email

# Features
Customizable URLs: Define your own base URL, parameters, and platform-specific links.
Fallback URL: If the app is not installed, users will be redirected to the App Store or Play Store.
Custom Parameters: Pass UTM parameters or other query parameters.
Simple and Extendable: Built with minimal dependencies and easy to extend.
# AgroSmart Android App

This is an Android WebView app that wraps the AgroSmart Flask website.

## Setup Instructions

1. Open this project in Android Studio.
2. Update the `websiteUrl` in `MainActivity.kt` to your actual website URL.
   - For local development on emulator: `http://10.0.2.2:5000`
   - For local development on device: Use your computer's IP address, e.g., `http://192.168.1.100:5000`
   - For production: Use your deployed website URL
3. Update the `network_security_config.xml` to include your domain.
5. Add app icons to `mipmap` folders (Android Studio can generate them) if needed.
6. If `gradle-wrapper.jar` is missing, open the project in Android Studio and sync to generate the wrapper.
7. Build and run the app.

## Features

- WebView wrapper for the website
- JavaScript enabled
- File upload support
- Back button navigation
- Loading progress bar
- External links open in browser
- No internet connection handling
- Splash screen with AgroSmart logo
- Mobile responsive (inherits from website)

## Permissions

- INTERNET: To load the website
- ACCESS_NETWORK_STATE: To check connectivity

## Notes

- The website code is not modified; this is purely a WebView wrapper.
- Ensure your Flask app allows CORS if needed for local testing.
- For production, deploy your Flask app and update the URL accordingly.
# CrediBot Android App + Python Backend Integration Guide

This guide explains how to set up and run the complete CrediBot system with both the Android
frontend and Python Flask backend.

## 🏗️ System Architecture

```
┌─────────────────┐     HTTP/REST API     ┌─────────────────┐
│                 │ ◄─────────────────────► │                 │
│  Android App    │                       │  Flask Backend  │
│  (Jetpack       │   • Chat Messages     │  (Python)       │
│   Compose)      │   • Language Setting  │                 │
│                 │   • Loan Questions    │                 │
│                 │   • Document Upload   │                 │
└─────────────────┘                       └─────────────────┘
                                                    │
                                                    ▼
                                          ┌─────────────────┐
                                          │                 │
                                          │  Google Gemini  │
                                          │  AI Service     │
                                          │                 │
                                          └─────────────────┘
```

## 📋 Prerequisites

### For Python Backend:

- Python 3.8 or higher
- pip (Python package manager)
- Google Gemini API key

### For Android App:

- Android Studio Arctic Fox or later
- Android SDK API 24+ (Android 7.0+)
- Android device or emulator

## 🚀 Setup Instructions

### Step 1: Python Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd python_backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   Create a `.env` file in the `python_backend` directory:
   ```env
   GEMINI_API_KEY=your_google_gemini_api_key_here
   ```

   Or set the environment variable directly:
   ```bash
   # Windows
   set GEMINI_API_KEY=your_google_gemini_api_key_here
   
   # macOS/Linux
   export GEMINI_API_KEY=your_google_gemini_api_key_here
   ```

5. **Start the Flask server:**
   ```bash
   python flask_api.py
   ```

   Or use the runner script:
   ```bash
   python run_server.py
   ```

   The server will start on `http://localhost:8000`

### Step 2: Android App Setup

1. **Open the project in Android Studio:**
    - Open Android Studio
    - Select "Open an existing project"
    - Navigate to the project root directory
    - Click "OK"

2. **Configure the backend URL:**

   In `app/src/main/java/com/runanywhere/startup_hackathon20/network/NetworkModule.kt`:

   ```kotlin
   // For Android emulator (default)
   private const val BASE_URL = "http://10.0.2.2:8000/"
   
   // For real Android device (replace with your computer's IP)
   private const val BASE_URL = "http://192.168.1.100:8000/"
   ```

3. **Find your computer's IP address:**

   ```bash
   # Windows
   ipconfig
   
   # macOS/Linux
   ifconfig
   ```

   Look for your local network IP (usually 192.168.x.x or 10.0.x.x)

4. **Sync the project:**
    - Click "Sync Project with Gradle Files" in Android Studio
    - Wait for the sync to complete

5. **Run the app:**
    - Connect an Android device or start an emulator
    - Click the "Run" button or press Shift+F10

## 🔧 Configuration Options

### Backend Configuration

In `python_backend/flask_api.py`, you can modify:

- **Port:** Change `port=8000` to your preferred port
- **Host:** Change `host='0.0.0.0'` to restrict access
- **API Keys:** Update the Gemini API key
- **Languages:** Add or modify supported languages in `LANGUAGES` dict
- **Loan Questions:** Customize questions in `LOAN_QUESTIONS` dict

### Android App Configuration

In `app/src/main/java/com/runanywhere/startup_hackathon20/network/NetworkModule.kt`:

- **Base URL:** Update to match your backend server
- **Timeouts:** Adjust connection and read timeouts
- **Logging:** Enable/disable HTTP request logging

## 🧪 Testing the Integration

### 1. Test Backend API

Test the backend endpoints using curl or a tool like Postman:

```bash
# Health check
curl http://localhost:8000/health

# Chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "languageCode": "en-IN"}'

# Translation endpoint
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello", "source_language_code": "en-IN", "target_language_code": "hi-IN"}'
```

### 2. Test Android App

1. **Language Selection:** Test switching between different languages
2. **Basic Chat:** Send simple messages and verify responses
3. **Loan Flow:** Try messages like "check loan eligibility" to trigger the loan questionnaire
4. **Document Upload:** Test the document upload feature
5. **Voice Features:** Test voice input (microphone button)

## 🔍 Troubleshooting

### Common Issues:

1. **"Connection refused" error in Android app:**
    - Ensure the Flask server is running
    - Check the BASE_URL in NetworkModule.kt
    - For real devices, use your computer's IP address

2. **"Network security policy" error:**
    - Add network security config to allow HTTP connections (for development)
    - Or use HTTPS in production

3. **Gemini API errors:**
    - Verify your API key is correct
    - Check if you have API quota/billing set up
    - Ensure internet connection is available

4. **Build errors in Android:**
    - Clean and rebuild the project
    - Check if all dependencies are properly synced
    - Verify Android SDK is properly installed

### Debug Logs:

**Backend logs:** Check the Flask server console for API request logs

**Android logs:** Use Android Studio's Logcat to view app logs:

- Filter by package name: `com.runanywhere.startup_hackathon20`
- Look for network-related logs with tag "OkHttp"

## 🚀 Production Deployment

### Backend Deployment:

1. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 flask_api:app
   ```

2. **Enable HTTPS** for secure communication

3. **Set up proper environment variables** on your server

4. **Use a reverse proxy** (nginx) for better performance

### Android App Deployment:

1. **Update BASE_URL** to your production server
2. **Enable network security** for HTTPS
3. **Build release APK** or publish to Google Play Store
4. **Test thoroughly** on different devices and network conditions

## 📱 Features Overview

### Available Features:

✅ **Multilingual Chat:** 11 Indian languages supported  
✅ **Loan Eligibility Assessment:** Step-by-step questionnaire  
✅ **Document Upload:** Process loan documents with AI  
✅ **Real-time Translation:** Translate messages between languages  
✅ **Voice Input:** Record voice messages (mock implementation)  
✅ **Text-to-Speech:** Play bot responses as audio (mock implementation)  
✅ **Smart Responses:** Context-aware AI responses using Gemini  
✅ **Dark/Light Themes:** Toggle between themes

### API Endpoints:

- `POST /chat` - Send chat messages
- `POST /translate` - Translate text between languages
- `POST /loan/start-questions` - Start loan eligibility flow
- `POST /loan/answer` - Submit loan question answers
- `POST /loan/check-eligibility` - Get loan eligibility results
- `POST /read-document` - Process uploaded documents
- `POST /set-language` - Set user language preference
- `GET /health` - Health check endpoint

## 🔮 Future Enhancements

1. **Real Speech Services:** Integrate Google Speech-to-Text and Text-to-Speech APIs
2. **Document OCR:** Add actual text extraction from images and PDFs
3. **User Authentication:** Add user accounts and session management
4. **Database Integration:** Store chat history and user preferences
5. **Push Notifications:** Send loan updates and reminders
6. **Advanced Analytics:** Track user interactions and improve responses
7. **Offline Mode:** Cache responses for basic functionality without internet

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs in both Android Studio and Flask server console
3. Ensure all dependencies are properly installed
4. Verify network connectivity between Android app and backend
5. Test API endpoints directly before testing through the app

---

**Happy Coding! 🎉**

The CrediBot system demonstrates modern mobile app development with AI integration, multilingual
support, and real-time communication between Android frontend and Python backend.
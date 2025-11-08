# Multilingual Chatbot Android App (CrediBot)

This Android application is a multilingual chatbot that supports 10 different Indian languages and
focuses on helping users with loan and financial queries. The app was converted from an HTML-based
chatbot to a native Android application using Jetpack Compose.

## Features

### 1. Language Selection Screen

- **Multi-brand Display**: CrediBot name animates through different languages (English, Hindi,
  Tamil, Telugu, Kannada, Malayalam)
- **10 Language Support**:
    - English
    - Hindi (हिन्दी)
    - Tamil (தமிழ்)
    - Telugu (తెలుగు)
    - Kannada (ಕನ್ನಡ)
    - Malayalam (മലയാളം)
    - Marathi (मराठी)
    - Bengali (বাংলা)
    - Gujarati (ગુજરાતી)
    - Punjabi (ਪੰਜਾਬੀ)
- **Dark/Light Theme Toggle**: Switch between themes using the toggle in the top bar
- **Telegram Bot Integration**: Quick access to Telegram bot option

### 2. Chat Interface

- **Multilingual Chat**: Intelligent responses in selected language
- **Modern UI**: Clean, Material Design 3 interface with rounded message bubbles
- **Real-time Language Switching**: Change language during conversation via dropdown
- **Typing Indicators**: Shows when bot is processing response
- **Auto-scroll**: Automatically scrolls to latest messages

### 3. Voice Features

- **Voice Input**: Tap microphone icon to record voice messages
- **Text-to-Speech**: Bot messages can be played as audio
- **Recording Indicator**: Visual feedback during voice recording

### 4. Document Upload

- **File Picker Integration**: Upload loan documents for analysis
- **Document Processing**: AI explains uploaded documents in selected language
- **Supported Formats**: Images and PDF files

### 5. Message Actions

- **Speak**: Convert any bot message to speech
- **Translate**: Translate messages between languages
- **Copy/Share**: Standard message interaction options

## Technical Implementation

### Architecture

- **MVVM Pattern**: Uses ChatViewModel for state management
- **Jetpack Compose**: Modern Android UI toolkit
- **Material Design 3**: Latest design system
- **Coroutines**: Asynchronous operations

### Key Components

1. **MainActivity**: Main entry point with TextToSpeech initialization
2. **ChatViewModel**: Manages chat state, messages, and language switching
3. **LanguageSelectionScreen**: Initial language selection interface
4. **ChatScreen**: Main chat interface
5. **MessageBubble**: Individual message display component
6. **TypingIndicator**: Shows bot is processing

### Data Models

- **ChatMessage**: Represents individual messages with user/bot flag
- **Language**: Contains language code, name, and native name

### Smart Response System

The chatbot provides contextual responses based on keywords:

- **Loan queries**: Information about different loan types
- **Documentation**: Required documents for loan applications
- **Eligibility**: Criteria for loan approval
- **Interest rates**: Current market rates for various loans
- **General assistance**: Comprehensive financial guidance

## Setup Instructions

### Prerequisites

- Android Studio Arctic Fox or later
- Android SDK API 24+ (Android 7.0+)
- Kotlin support

### Build Instructions

1. Open project in Android Studio
2. Sync Gradle files
3. Run the app on device/emulator

```bash
./gradlew assembleDebug
```

### Permissions Required

- `RECORD_AUDIO`: For voice input functionality
- `READ_EXTERNAL_STORAGE`: For document upload
- `READ_MEDIA_IMAGES`: For image selection (Android 13+)
- `INTERNET`: For potential API calls
- `ACCESS_NETWORK_STATE`: Network connectivity checks

## Usage Guide

### Getting Started

1. **Launch App**: Open the CrediBot application
2. **Select Language**: Choose your preferred language from the grid
3. **Start Chatting**: Begin conversation with the multilingual assistant

### Chat Features

1. **Text Input**: Type messages in the text field and tap Send
2. **Voice Input**: Tap microphone icon, speak, and release
3. **Document Upload**: Tap "Upload Loan Document" to select files
4. **Language Switch**: Use dropdown in header to change language
5. **Message Actions**: Tap Speak or Translate buttons on bot messages

### Best Practices

- **Clear Speech**: Speak clearly when using voice input
- **Relevant Documents**: Upload clear, relevant loan documents
- **Language Context**: The bot maintains context across language switches
- **Specific Queries**: Ask specific questions for better responses

## Customization

### Adding New Languages

1. Update `availableLanguages` list in MainActivity
2. Add language-specific responses in ChatViewModel
3. Update brand text animation cycle

### Modifying Responses

- Edit `generateMockResponse()` function in ChatViewModel
- Add new keyword patterns and responses
- Enhance context understanding

### UI Customization

- Modify colors in the Color scheme
- Adjust layouts in Composable functions
- Update animation timing and effects

## Future Enhancements

### Planned Features

1. **Real API Integration**: Connect to actual AI/ML services
2. **Voice Recognition**: Implement real speech-to-text
3. **Advanced OCR**: Better document text extraction
4. **Push Notifications**: Message alerts and reminders
5. **User Profiles**: Personalized loan recommendations
6. **Chat History**: Persistent conversation storage
7. **Offline Mode**: Basic functionality without internet

### Technical Improvements

1. **Database Integration**: Room database for chat history
2. **Network Layer**: Retrofit for API communications
3. **Image Processing**: Enhanced document analysis
4. **Security**: End-to-end encryption for sensitive data
5. **Performance**: Lazy loading and caching

## Troubleshooting

### Common Issues

1. **Build Errors**: Ensure all dependencies are properly synced
2. **Permission Issues**: Grant required permissions in app settings
3. **Voice Not Working**: Check microphone permissions
4. **File Upload Fails**: Verify storage permissions

### Debug Mode

Enable debug logging by modifying the log level in the application class.

## Contributing

### Development Setup

1. Fork the repository
2. Create feature branch
3. Make changes with proper testing
4. Submit pull request with detailed description

### Code Style

- Follow Kotlin coding conventions
- Use meaningful variable and function names
- Add comments for complex logic
- Maintain consistent formatting

## License

This project is part of a hackathon submission and includes features for multilingual loan
assistance. The application demonstrates modern Android development practices while providing
practical financial guidance functionality.

## Support

For technical support or feature requests, please refer to the project documentation or contact the
development team.

---
**Note**: This application currently uses mock responses for demonstration purposes. For production
use, integrate with actual AI/ML services and financial data providers.

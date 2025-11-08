package com.runanywhere.startup_hackathon20

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.State
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import com.runanywhere.startup_hackathon20.network.*
import android.content.Context
import android.media.MediaPlayer
import android.media.MediaRecorder
import android.util.Log
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.util.UUID
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody

// Simple Message Data Class for the multilingual chatbot
data class ChatMessage(
    val text: String,
    val isUser: Boolean,
    val timestamp: Long = System.currentTimeMillis(),
    val hasAudio: Boolean = false,
    val audioPath: String? = null
)

// Language data class
data class Language(
    val code: String,
    val name: String,
    val nativeName: String
)

// ViewModel for the multilingual chatbot with real API integration
class ChatViewModel : ViewModel() {

    private val apiService = NetworkModule.apiService
    private val userId = UUID.randomUUID().toString()
    private var mediaPlayer: MediaPlayer? = null
    private var mediaRecorder: MediaRecorder? = null
    private var audioFile: File? = null

    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _currentLanguage = MutableStateFlow<Language?>(null)
    val currentLanguage: StateFlow<Language?> = _currentLanguage

    private val _isRecording = MutableStateFlow(false)
    val isRecording: StateFlow<Boolean> = _isRecording

    private val _isTyping = MutableStateFlow(false)
    val isTyping: StateFlow<Boolean> = _isTyping

    private val _isPlayingAudio = MutableStateFlow(false)
    val isPlayingAudio: StateFlow<Boolean> = _isPlayingAudio

    init {
        // Initialize with welcome message
        _messages.value = listOf(
            ChatMessage("Hello! How can I assist you today?", false)
        )
    }

    fun setLanguage(language: Language) {
        _currentLanguage.value = language

        viewModelScope.launch {
            try {
                // Set language on backend
                val response = apiService.setLanguage(
                    mapOf("language_code" to language.code)
                )

                if (response.isSuccessful) {
                    // Send greeting in selected language
                    sendGreeting(language)
                }
            } catch (e: Exception) {
                // Fallback to local greeting
                val currentMessages = _messages.value.toMutableList()
                currentMessages.add(
                    ChatMessage(
                        "Language changed to ${language.nativeName}. How can I help you with your financial queries?",
                        false
                    )
                )
                _messages.value = currentMessages
            }
        }
    }

    private suspend fun sendGreeting(language: Language) {
        try {
            val response = apiService.sendMessage(
                ChatRequest(
                    message = "initial_greeting",
                    languageCode = language.code,
                    userId = userId,
                    isGreeting = true
                )
            )

            if (response.isSuccessful) {
                val chatResponse = response.body()
                chatResponse?.let {
                    val currentMessages = _messages.value.toMutableList()
                    currentMessages.add(ChatMessage(it.response, false))
                    _messages.value = currentMessages
                    // Generate and play TTS for greeting
                    playTextToSpeech(it.response, null)
                }
            } else {
                // Fallback greeting
                val currentMessages = _messages.value.toMutableList()
                currentMessages.add(
                    ChatMessage(
                        "Hello! I'm CrediBot, your multilingual loan assistant. How can I help you today?",
                        false
                    )
                )
                _messages.value = currentMessages
            }
        } catch (e: Exception) {
            // Fallback greeting
            val currentMessages = _messages.value.toMutableList()
            currentMessages.add(
                ChatMessage(
                    "Hello! I'm CrediBot, your multilingual loan assistant. How can I help you today?",
                    false
                )
            )
            _messages.value = currentMessages
        }
    }

    fun sendMessage(text: String) {
        // Add user message
        val currentMessages = _messages.value.toMutableList()
        currentMessages.add(ChatMessage(text, true))
        _messages.value = currentMessages

        viewModelScope.launch {
            _isLoading.value = true
            _isTyping.value = true

            try {
                val language = _currentLanguage.value
                val response = apiService.sendMessage(
                    ChatRequest(
                        message = text,
                        languageCode = language?.code ?: "en-IN",
                        userId = userId,
                        isGreeting = false
                    )
                )

                if (response.isSuccessful) {
                    val chatResponse = response.body()
                    chatResponse?.let {
                        val updatedMessages = _messages.value.toMutableList()
                        updatedMessages.add(ChatMessage(it.response, false))
                        _messages.value = updatedMessages
                        // Play TTS for bot response
                        playTextToSpeech(it.response, null)
                    }
                } else {
                    // Fallback response
                    val errorMessages = _messages.value.toMutableList()
                    errorMessages.add(
                        ChatMessage(
                            "I apologize, but I'm experiencing technical difficulties. Please try again.",
                            false
                        )
                    )
                    _messages.value = errorMessages
                }

            } catch (e: Exception) {
                val errorMessages = _messages.value.toMutableList()
                errorMessages.add(
                    ChatMessage(
                        "Sorry, I encountered an error. Please try again.",
                        false
                    )
                )
                _messages.value = errorMessages
            } finally {
                _isLoading.value = false
                _isTyping.value = false
            }
        }
    }

    fun translateMessage(message: String, targetLanguage: Language) {
        viewModelScope.launch {
            try {
                val currentLanguage = _currentLanguage.value
                if (currentLanguage?.code == targetLanguage.code) return@launch

                val response = apiService.translateText(
                    TranslateRequest(
                        input = message,
                        sourceLanguageCode = currentLanguage?.code ?: "en-IN",
                        targetLanguageCode = targetLanguage.code
                    )
                )

                if (response.isSuccessful) {
                    val translateResponse = response.body()
                    translateResponse?.let {
                        if (it.success) {
                            // Add translated message to chat
                            val currentMessages = _messages.value.toMutableList()
                            currentMessages.add(
                                ChatMessage(
                                    "🔄 Translation: ${it.translatedText}",
                                    false
                                )
                            )
                            _messages.value = currentMessages
                        }
                    }
                }
            } catch (e: Exception) {
                // Handle translation error silently
            }
        }
    }

    fun processDocumentUpload(fileName: String) {
        val currentMessages = _messages.value.toMutableList()
        currentMessages.add(ChatMessage("Document '$fileName' uploaded successfully.", false))

        viewModelScope.launch {
            try {
                _isTyping.value = true

                val language = _currentLanguage.value
                val response = apiService.processDocument(
                    DocumentRequest(
                        documentText = "Sample document content", // In real app, extract text from file
                        languageCode = language?.code ?: "en-IN",
                        fileType = "pdf"
                    )
                )

                if (response.isSuccessful) {
                    val docResponse = response.body()
                    docResponse?.let {
                        if (it.success) {
                            currentMessages.add(ChatMessage(it.vernacularExplanation, false))
                        } else {
                            currentMessages.add(
                                ChatMessage(
                                    "I was unable to process the document. Please ensure the document is clear and try again.",
                                    false
                                )
                            )
                        }
                    }
                } else {
                    currentMessages.add(
                        ChatMessage(
                            "There was an error processing your document. Please try again.",
                            false
                        )
                    )
                }

                _messages.value = currentMessages
            } catch (e: Exception) {
                currentMessages.add(
                    ChatMessage(
                        "Error processing document. Please check your connection and try again.",
                        false
                    )
                )
                _messages.value = currentMessages
            } finally {
                _isTyping.value = false
            }
        }
    }

    fun startRecording(context: Context) {
        try {
            // Create audio file
            audioFile = File(context.cacheDir, "recorded_audio_${System.currentTimeMillis()}.wav")

            mediaRecorder = MediaRecorder().apply {
                setAudioSource(MediaRecorder.AudioSource.MIC)
                setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP)
                setOutputFile(audioFile?.absolutePath)
                setAudioEncoder(MediaRecorder.AudioEncoder.AMR_NB)

                prepare()
                start()
            }

            _isRecording.value = true
            Log.d("ChatViewModel", "Recording started")

        } catch (e: Exception) {
            Log.e("ChatViewModel", "Error starting recording: ${e.message}")
            _isRecording.value = false
        }
    }

    fun stopRecording() {
        try {
            mediaRecorder?.apply {
                stop()
                release()
            }
            mediaRecorder = null
            _isRecording.value = false

            // Process the recorded audio
            audioFile?.let { file ->
                processRecordedAudio(file)
            }

            Log.d("ChatViewModel", "Recording stopped")

        } catch (e: Exception) {
            Log.e("ChatViewModel", "Error stopping recording: ${e.message}")
            _isRecording.value = false
        }
    }

    private fun processRecordedAudio(audioFile: File) {
        viewModelScope.launch {
            try {
                _isLoading.value = true

                // Create multipart body for audio file
                val requestBody = audioFile.asRequestBody()
                val audioPart =
                    MultipartBody.Part.createFormData("audio", audioFile.name, requestBody)

                val response = apiService.speechToText(audioPart)

                if (response.isSuccessful) {
                    val sttResponse = response.body()
                    sttResponse?.let { result ->
                        if (result.response.isNotBlank()) {
                            // Send the transcribed text as a message
                            sendMessage(result.response)
                        } else {
                            addErrorMessage("Could not understand the audio. Please try again.")
                        }
                    }
                } else {
                    Log.e("ChatViewModel", "STT failed: ${response.code()}")
                    addErrorMessage("Speech recognition failed. Please try typing your message.")
                }

            } catch (e: Exception) {
                Log.e("ChatViewModel", "STT error: ${e.message}")
                addErrorMessage("Speech recognition error. Please try again.")
            } finally {
                _isLoading.value = false
                // Clean up audio file
                audioFile.delete()
            }
        }
    }

    private fun addErrorMessage(message: String) {
        val errorMessages = _messages.value.toMutableList()
        errorMessages.add(ChatMessage(message, false))
        _messages.value = errorMessages
    }

    fun playTextToSpeech(text: String, context: Context?) {
        viewModelScope.launch {
            try {
                _isPlayingAudio.value = true

                val response = apiService.textToSpeech(
                    TextToSpeechRequest(
                        inputs = listOf(text),
                        targetLanguageCode = _currentLanguage.value?.code ?: "en-IN"
                    )
                )

                if (response.isSuccessful) {
                    val audioData = response.body()?.bytes()
                    audioData?.let { data ->
                        playAudioFromBytes(data, context)
                    }
                } else {
                    Log.e("ChatViewModel", "TTS failed: ${response.code()}")
                    _isPlayingAudio.value = false
                }
            } catch (e: Exception) {
                Log.e("ChatViewModel", "TTS error: ${e.message}")
                _isPlayingAudio.value = false
            }
        }
    }

    private fun playAudioFromBytes(audioData: ByteArray, context: Context?) {
        try {
            // Stop any existing playback
            stopAudio()

            // Create temporary file for audio
            context?.let { ctx ->
                val tempFile = File.createTempFile("tts_audio", ".wav", ctx.cacheDir)
                FileOutputStream(tempFile).use { fos ->
                    fos.write(audioData)
                }

                // Create and configure MediaPlayer
                mediaPlayer = MediaPlayer().apply {
                    setDataSource(tempFile.absolutePath)
                    setOnPreparedListener { mp ->
                        mp.start()
                    }
                    setOnCompletionListener {
                        _isPlayingAudio.value = false
                        tempFile.delete() // Clean up temp file
                    }
                    setOnErrorListener { _, _, _ ->
                        _isPlayingAudio.value = false
                        tempFile.delete()
                        true
                    }
                    prepareAsync()
                }
            } ?: run {
                _isPlayingAudio.value = false
            }
        } catch (e: Exception) {
            Log.e("ChatViewModel", "Audio playback error: ${e.message}")
            _isPlayingAudio.value = false
        }
    }

    fun stopAudio() {
        mediaPlayer?.let { mp ->
            if (mp.isPlaying) {
                mp.stop()
            }
            mp.release()
        }
        mediaPlayer = null
        _isPlayingAudio.value = false
    }

    fun clearMessages() {
        _messages.value = listOf(
            ChatMessage("Hello! How can I assist you today?", false)
        )
    }

    override fun onCleared() {
        super.onCleared()
        stopAudio()
        mediaRecorder?.release()
        mediaRecorder = null
    }
}

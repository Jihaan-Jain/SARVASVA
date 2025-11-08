package com.runanywhere.startup_hackathon20.network

import retrofit2.Response
import retrofit2.http.*
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.ResponseBody

// Data classes for API requests and responses
data class ChatRequest(
    val message: String,
    val languageCode: String,
    val userId: String? = null,
    val isGreeting: Boolean = false
)

data class ChatResponse(
    val response: String,
    val success: Boolean,
    val error: String? = null
)

data class TranslateRequest(
    val input: String,
    val sourceLanguageCode: String,
    val targetLanguageCode: String
)

data class TranslateResponse(
    val translatedText: String,
    val success: Boolean,
    val error: String? = null
)

data class DocumentRequest(
    val documentText: String,
    val languageCode: String,
    val fileType: String
)

data class DocumentResponse(
    val vernacularExplanation: String,
    val success: Boolean,
    val error: String? = null
)

data class TextToSpeechRequest(
    val inputs: List<String>,
    val targetLanguageCode: String = "en-IN",
    val speaker: String? = null
)

interface ApiService {

    @POST("chat")
    suspend fun sendMessage(@Body request: ChatRequest): Response<ChatResponse>

    @POST("translate")
    suspend fun translateText(@Body request: TranslateRequest): Response<TranslateResponse>

    @POST("text-to-speech")
    suspend fun textToSpeech(@Body request: TextToSpeechRequest): Response<ResponseBody>

    @POST("speech-to-text")
    @Multipart
    suspend fun speechToText(@Part audio: MultipartBody.Part): Response<ChatResponse>

    @POST("read-document")
    suspend fun processDocument(@Body request: DocumentRequest): Response<DocumentResponse>

    @POST("set-language")
    suspend fun setLanguage(@Body request: Map<String, String>): Response<Map<String, Any>>
}
package com.runanywhere.startup_hackathon20

import android.Manifest
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import kotlinx.coroutines.delay
import java.util.*

// Language options matching the HTML
val availableLanguages = listOf(
    Language("en-IN", "English", "English"),
    Language("hi-IN", "Hindi", "हिन्दी"),
    Language("ta-IN", "Tamil", "தமிழ்"),
    Language("te-IN", "Telugu", "తెలుగు"),
    Language("kn-IN", "Kannada", "ಕನ್ನಡ"),
    Language("ml-IN", "Malayalam", "മലയാളം"),
    Language("mr-IN", "Marathi", "मराठी"),
    Language("bn-IN", "Bengali", "বাংলা"),
    Language("gu-IN", "Gujarati", "ગુજરાતી"),
    Language("pa-IN", "Punjabi", "ਪੰਜਾਬੀ")
)

class MainActivity : ComponentActivity(), TextToSpeech.OnInitListener {
    private var textToSpeech: TextToSpeech? = null
    private val RECORD_AUDIO_PERMISSION_REQUEST = 100
    private val READ_STORAGE_PERMISSION_REQUEST = 101

    private val audioPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val recordAudioGranted = permissions[Manifest.permission.RECORD_AUDIO] ?: false
        if (!recordAudioGranted) {
            // Handle permission denied
            Toast.makeText(
                this,
                "Audio recording permission is required for speech functionality",
                Toast.LENGTH_LONG
            ).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize TextToSpeech
        textToSpeech = TextToSpeech(this, this)

        // Request audio permissions
        requestAudioPermissions()

        setContent {
            MaterialTheme {
                CrediBot()
            }
        }
    }

    private fun requestAudioPermissions() {
        val permissions = arrayOf(
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.MODIFY_AUDIO_SETTINGS
        )

        val missingPermissions = permissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }

        if (missingPermissions.isNotEmpty()) {
            audioPermissionLauncher.launch(missingPermissions.toTypedArray())
        }
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            textToSpeech?.language = Locale.US
        }
    }

    override fun onDestroy() {
        textToSpeech?.shutdown()
        super.onDestroy()
    }

    fun checkAndRequestPermission(permission: String, requestCode: Int): Boolean {
        return if (ContextCompat.checkSelfPermission(
                this,
                permission
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(this, arrayOf(permission), requestCode)
            false
        } else {
            true
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CrediBot() {
    var selectedLanguage by remember { mutableStateOf<Language?>(null) }
    var showLanguageSelection by remember { mutableStateOf(true) }
    var isDarkTheme by remember { mutableStateOf(false) }
    var brandTextIndex by remember { mutableStateOf(0) }
    val chatViewModel: ChatViewModel = viewModel()

    // Animate brand text
    LaunchedEffect(Unit) {
        while (true) {
            delay(3000)
            brandTextIndex++
        }
    }

    if (showLanguageSelection) {
        // Show language selection
        LanguageSelectionScreen(
            onLanguageSelected = { language ->
                selectedLanguage = language
                showLanguageSelection = false
                chatViewModel.setLanguage(language)
            },
            brandTextIndex = brandTextIndex,
            onNavigateBack = { }
        )
    } else {
        // Show main chat content
        selectedLanguage?.let { language ->
            ChatScreen(
                language = language,
                isDarkTheme = isDarkTheme,
                onThemeToggle = { isDarkTheme = !isDarkTheme },
                brandTextIndex = brandTextIndex,
                chatViewModel = chatViewModel,
                onNavigateBack = {
                    selectedLanguage = null
                    showLanguageSelection = true
                }
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LanguageSelectionScreen(
    isDarkTheme: Boolean = false,
    onThemeToggle: () -> Unit = {},
    onLanguageSelected: (Language) -> Unit,
    brandTextIndex: Int,
    onNavigateBack: () -> Unit
) {
    val currentBrandText = when (brandTextIndex % 6) {
        0 -> "CrediBot"
        1 -> "क्रेडिबॉट"
        2 -> "கிரெடிபாட்"
        3 -> "క్రెడిబాట్"
        4 -> "ಕ್ರೆಡಿಬಾಟ್"
        5 -> "ക്രെഡിബോട്ട്"
        else -> "CrediBot"
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(if (isDarkTheme) Color(0xFF111827) else Color(0xFFF5F7FB))
    ) {
        // Top Navigation
        TopAppBar(
            title = {
                Box(
                    modifier = Modifier.fillMaxWidth(),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = currentBrandText,
                        fontSize = 32.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (isDarkTheme) Color.White else Color.Black
                    )
                }
            },
            actions = {
                // Theme Toggle
                Switch(
                    checked = isDarkTheme,
                    onCheckedChange = { onThemeToggle() },
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = Color(0xFF4F46E5),
                        uncheckedThumbColor = Color.Gray
                    )
                )
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = Color.White
            )
        )

        // Main Content
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = if (isDarkTheme) Color(0xFF1F2937) else Color.White
                ),
                elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
            ) {
                Column(
                    modifier = Modifier.padding(30.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    // Logo
                    Box(
                        modifier = Modifier
                            .size(80.dp)
                            .clip(RoundedCornerShape(20.dp))
                            .background(Color(0xFF4F46E5).copy(alpha = 0.1f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Home,
                            contentDescription = "Logo",
                            modifier = Modifier.size(48.dp),
                            tint = Color(0xFF4F46E5)
                        )
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    Text(
                        text = "Multilingual Assistant",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (isDarkTheme) Color.White else Color.Black
                    )

                    Spacer(modifier = Modifier.height(24.dp))

                    Text(
                        text = "Welcome! Please select your preferred language to start the conversation.",
                        fontSize = 16.sp,
                        textAlign = TextAlign.Center,
                        color = if (isDarkTheme) Color(0xFF9CA3AF) else Color(0xFF6B7280)
                    )

                    Spacer(modifier = Modifier.height(24.dp))

                    // Language Grid
                    for (i in availableLanguages.indices step 2) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 8.dp),
                            horizontalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            LanguageButton(
                                language = availableLanguages[i],
                                isDarkTheme = isDarkTheme,
                                modifier = Modifier.weight(1f),
                                onClick = { onLanguageSelected(availableLanguages[i]) }
                            )
                            
                            if (i + 1 < availableLanguages.size) {
                                LanguageButton(
                                    language = availableLanguages[i + 1],
                                    isDarkTheme = isDarkTheme,
                                    modifier = Modifier.weight(1f),
                                    onClick = { onLanguageSelected(availableLanguages[i + 1]) }
                                )
                            } else {
                                Spacer(modifier = Modifier.weight(1f))
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(20.dp))

                    // Telegram Button
                    OutlinedButton(
                        onClick = { /* Handle Telegram link */ },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.outlinedButtonColors(
                            contentColor = Color(0xFF4F46E5)
                        )
                    ) {
                        Text("Telegram Bot")
                    }
                }
            }
        }
    }
}

@Composable
fun LanguageButton(
    language: Language,
    isDarkTheme: Boolean,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    Card(
        modifier = modifier
            .height(100.dp)
            .clickable { onClick() },
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isDarkTheme) Color(0xFF374151) else Color.White
        ),
        border = CardDefaults.outlinedCardBorder()
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = language.name,
                fontSize = 14.sp,
                color = if (isDarkTheme) Color(0xFF9CA3AF) else Color(0xFF6B7280)
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = language.nativeName,
                fontSize = 18.sp,
                fontWeight = FontWeight.SemiBold,
                color = if (isDarkTheme) Color.White else Color.Black
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(
    language: Language,
    isDarkTheme: Boolean,
    onThemeToggle: () -> Unit,
    brandTextIndex: Int,
    chatViewModel: ChatViewModel,
    onNavigateBack: () -> Unit
) {
    val context = LocalContext.current
    var messageText by remember { mutableStateOf("") }
    val messages by chatViewModel.messages.collectAsState()
    val isTyping by chatViewModel.isTyping.collectAsState()
    val isRecording by chatViewModel.isRecording.collectAsState()
    val listState = rememberLazyListState()

    // File picker launcher
    val filePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            // Handle document upload
            Toast.makeText(context, "Document selected: $uri", Toast.LENGTH_SHORT).show()
            chatViewModel.processDocumentUpload(uri.lastPathSegment ?: "document")
        }
    }

    // Auto-scroll to bottom
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.size - 1)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(if (isDarkTheme) Color(0xFF111827) else Color(0xFFF5F7FB))
    ) {
        // Chat Header
        TopAppBar(
            title = {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .background(Color.White.copy(alpha = 0.2f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Home,
                            contentDescription = "Logo",
                            modifier = Modifier.size(24.dp),
                            tint = Color.White
                        )
                    }
                    Text(
                        text = "Multilingual Assistant",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color.White
                    )
                }
            },
            navigationIcon = {
                IconButton(onClick = onNavigateBack) {
                    Icon(
                        imageVector = Icons.Default.Home,
                        contentDescription = "Back to Eligibility"
                    )
                }
            },
            actions = {
                // Language Selector Dropdown
                var expanded by remember { mutableStateOf(false) }
                
                Box {
                    TextButton(
                        onClick = { expanded = true },
                        colors = ButtonDefaults.textButtonColors(contentColor = Color.White)
                    ) {
                        Text("${language.nativeName} ▼")
                    }
                    
                    DropdownMenu(
                        expanded = expanded,
                        onDismissRequest = { expanded = false }
                    ) {
                        availableLanguages.forEach { lang ->
                            DropdownMenuItem(
                                text = { Text("${lang.name} (${lang.nativeName})") },
                                onClick = {
                                    chatViewModel.setLanguage(lang)
                                    expanded = false
                                }
                            )
                        }
                    }
                }
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = Color(0xFF4F46E5)
            )
        )

        // Messages List
        LazyColumn(
            state = listState,
            modifier = Modifier.weight(1f),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            items(messages) { message ->
                MessageBubble(message = message, isDarkTheme = isDarkTheme)
            }
            
            // Typing indicator
            if (isTyping) {
                item {
                    TypingIndicator(isDarkTheme = isDarkTheme)
                }
            }
        }

        // Input Area
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            colors = CardDefaults.cardColors(
                containerColor = if (isDarkTheme) Color(0xFF1F2937) else Color.White
            ),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                // Document Upload Button
                OutlinedButton(
                    onClick = {
                        filePickerLauncher.launch("*/*")
                    },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = Color(0xFF4F46E5)
                    )
                ) {
                    Icon(
                        imageVector = Icons.Default.Add,
                        contentDescription = "Upload",
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Upload Loan Document")
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Input Row
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.Bottom
                ) {
                    // Text Input
                    OutlinedTextField(
                        value = messageText,
                        onValueChange = { messageText = it },
                        modifier = Modifier.weight(1f),
                        placeholder = { Text("Type your message here...") },
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Color(0xFF4F46E5),
                            focusedLabelColor = Color(0xFF4F46E5)
                        )
                    )

                    // Send Button
                    FloatingActionButton(
                        onClick = {
                            if (messageText.trim().isNotEmpty()) {
                                chatViewModel.sendMessage(messageText)
                                messageText = ""
                            }
                        },
                        containerColor = Color(0xFF4F46E5),
                        modifier = Modifier.size(48.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Send,
                            contentDescription = "Send",
                            tint = Color.White
                        )
                    }
                }

                // Voice Controls
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    // Speech-to-Text (Listen) Button
                    val isRecording by chatViewModel.isRecording.collectAsState()
                    IconButton(
                        onClick = {
                            if (isRecording) {
                                chatViewModel.stopRecording()
                            } else {
                                chatViewModel.startRecording(context)
                            }
                        }
                    ) {
                        Icon(
                            imageVector = if (isRecording) Icons.Default.Stop else Icons.Default.Mic,
                            contentDescription = if (isRecording) "Stop Recording" else "Start Recording",
                            tint = if (isRecording) Color.Red else MaterialTheme.colorScheme.primary
                        )
                    }

                    // Text-to-Speech (Speak) Button for last message
                    val isPlayingAudio by chatViewModel.isPlayingAudio.collectAsState()
                    IconButton(
                        onClick = {
                            if (isPlayingAudio) {
                                chatViewModel.stopAudio()
                            } else {
                                // Play TTS for the last bot message
                                val lastBotMessage = messages.lastOrNull { !it.isUser }
                                lastBotMessage?.let { message ->
                                    chatViewModel.playTextToSpeech(message.text, context)
                                }
                            }
                        }
                    ) {
                        Icon(
                            imageVector = if (isPlayingAudio) Icons.Default.VolumeOff else Icons.Default.VolumeUp,
                            contentDescription = if (isPlayingAudio) "Stop Audio" else "Play Audio",
                            tint = if (isPlayingAudio) Color.Red else MaterialTheme.colorScheme.primary
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun MessageBubble(message: ChatMessage, isDarkTheme: Boolean) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (message.isUser) Arrangement.End else Arrangement.Start
    ) {
        Card(
            modifier = Modifier.widthIn(max = 280.dp),
            shape = RoundedCornerShape(
                topStart = 18.dp,
                topEnd = 18.dp,
                bottomStart = if (message.isUser) 18.dp else 4.dp,
                bottomEnd = if (message.isUser) 4.dp else 18.dp
            ),
            colors = CardDefaults.cardColors(
                containerColor = if (message.isUser) {
                    Color(0xFF4F46E5)
                } else {
                    if (isDarkTheme) Color(0xFF374151) else Color(0xFFF0F0F0)
                }
            ),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = message.text,
                    color = if (message.isUser) Color.White else {
                        if (isDarkTheme) Color.White else Color.Black
                    },
                    fontSize = 16.sp,
                    lineHeight = 22.sp
                )
                
                // Action buttons for bot messages
                if (!message.isUser) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        TextButton(
                            onClick = { /* Handle speak */ },
                            colors = ButtonDefaults.textButtonColors(
                                contentColor = Color(0xFF4F46E5)
                            )
                        ) {
                            Icon(
                                imageVector = Icons.Default.PlayArrow,
                                contentDescription = "Speak",
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("Speak", fontSize = 12.sp)
                        }
                        
                        TextButton(
                            onClick = { /* Handle translate */ },
                            colors = ButtonDefaults.textButtonColors(
                                contentColor = Color(0xFF4F46E5)
                            )
                        ) {
                            Icon(
                                imageVector = Icons.Default.Settings,
                                contentDescription = "Translate",
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("Translate", fontSize = 12.sp)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun TypingIndicator(isDarkTheme: Boolean) {
    Card(
        modifier = Modifier.widthIn(max = 100.dp),
        shape = RoundedCornerShape(18.dp, 18.dp, 18.dp, 4.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isDarkTheme) Color(0xFF374151) else Color(0xFFF0F0F0)
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(5.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            repeat(3) {
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .clip(CircleShape)
                        .background(if (isDarkTheme) Color(0xFF9CA3AF) else Color(0xFF6B7280))
                )
            }
        }
    }
}
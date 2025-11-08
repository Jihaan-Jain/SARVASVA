import os
import random
import uuid
import requests
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import google.generativeai as genai
import tempfile
import base64
from io import BytesIO

app = Flask(__name__)
CORS(app)

# API Keys - Replace with your actual keys
GEMINI_API_KEY = "AIzaSyC9i96-x18BGKIeV7HOHKn-piu4e5R9IUs"
SARVAM_API_KEY = "d60e2e18-3b3c-492d-8faf-7f9db7c55201"

# Configure Gemini API
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Gemini API initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Gemini API: {e}")
    model = None

# Generation configuration
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 1024
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    }
]

# Supported Languages
LANGUAGES = {
    "en-IN": "English",
    "hi-IN": "Hindi",
    "bn-IN": "Bengali", 
    "gu-IN": "Gujarati",
    "kn-IN": "Kannada",
    "ml-IN": "Malayalam",
    "mr-IN": "Marathi",
    "od-IN": "Odia",
    "pa-IN": "Punjabi",
    "ta-IN": "Tamil",
    "te-IN": "Telugu"
}

# Complete loan questions in all languages (from bot1.py)
LOAN_QUESTIONS = {
    "en-IN": [
        "How many dependents do you have?",
        "For how many months do you need the loan?",
        "Are you a graduate or non-graduate?",
        "What is your annual income?",
        "What is your residential asset value?",
        "What is your commercial asset value?",
        "Are you self-employed?",
        "What is the loan amount you require?",
        "What type of loan are you looking for?",
        "What is the value of your luxury assets?",
        "What is your total bank asset value?"
    ],
    "hi-IN": [
        "आपके कितने आश्रित हैं?",
        "आप कितने महीनों के लिए ऋण चाहते हैं?",
        "क्या आप स्नातक हैं या गैर-स्नातक?",
        "आपकी वार्षिक आय कितनी है?",
        "आपकी आवासीय संपत्ति का मूल्य क्या है?",
        "आपकी व्यावसायिक संपत्ति का मूल्य क्या है?",
        "क्या आप स्वरोजगार करते हैं?",
        "आपको कितनी ऋण राशि चाहिए?",
        "आप किस प्रकार का ऋण चाहते हैं?",
        "आपकी लक्ज़री संपत्ति का मूल्य कितना है?",
        "आपकी कुल बैंक संपत्ति का मूल्य कितना है?"
    ],
    "bn-IN": [
        "আপনার কতজন নির্ভরশীল রয়েছে?",
        "আপনাকে কত মাসের জন্য ঋণের প্রয়োজন?",
        "আপনি স্নাতক না অস্নাতক?",
        "আপনার বার্ষিক আয় কত?",
        "আপনার আবাসিক সম্পত্তির মূল্য কত?",
        "আপনার বাণিজ্যিক সম্পত্তির মূল্য কত?",
        "আপনি কি স্বনিযুক্ত?",
        "আপনার কত ঋণের পরিমাণ প্রয়োজন?",
        "আপনি কী ধরনের ঋণ খুঁজছেন?",
        "আপনার বিলাসবহুল সম্পত্তির মূল্য কত?",
        "আপনার মোট ব্যাংক সম্পদের মূল্য কত?"
    ],
    "gu-IN": [
        "તમારા કેટલા આધારિત સભ્યો છે?",
        "તમારે કેટલા મહિના માટે લોનની જરૂર છે?",
        "શું તમે સ્નાતક છો કે નહીં?",
        "તમારી વાર્ષિક આવક કેટલી છે?",
        "તમારા રહેવાસી સંપત્તિનું મૂલ્ય શું છે?",
        "તમારા વ્યાપારી સંપત્તિનું મૂલ્ય શું છે?",
        "શું તમે સ્વરોજગાર છો?",
        "તમારે કેટલી લોનની રકમની જરૂર છે?",
        "તમે કયા પ્રકારની લોન માટે જોઈ રહ્યા છો?",
        "તમારા વૈભવી સંપત્તિનું મૂલ્ય શું છે?",
        "તમારા કુલ બેંક સંપત્તિનું મૂલ્ય શું છે?"
    ],
    "kn-IN": [
        "ನೀವು ಎಷ್ಟು ಅವಲಂಬಿತರನ್ನು ಹೊಂದಿದ್ದಾರೆ?",
        "ನೀವು ಎಷ್ಟು ತಿಂಗಳು ಸಾಲ ಬೇಕು?",
        "ನೀವು ಪದವೀಧರರಾಗಿದ್ದೀರಾ ಅಥವಾ ಪದವೀಧರರಲ್ಲ?",
        "ನಿಮ್ಮ ವಾರ್ಷಿಕ ಆದಾಯ ಎಷ್ಟು?",
        "ನಿಮ್ಮ ನಿವಾಸ ಆಸ್ತಿಯ ಮೌಲ್ಯ ಎಷ್ಟು?",
        "ನಿಮ್ಮ ವಾಣಿಜ್ಯ ಆಸ್ತಿಯ ಮೌಲ್ಯ ಎಷ್ಟು?",
        "ನೀವು ಸ್ವಾವಲಂಬಿಯಾಗಿ ಉದ್ಯೋಗದಲ್ಲಿದ್ದೀರಾ?",
        "ನೀವು ಎಷ್ಟು ಸಾಲದ ಮೊತ್ತವನ್ನು ಅಗತ್ಯವಿದೆ?",
        "ನೀವು ಯಾವ ರೀತಿಯ ಸಾಲವನ್ನು ಹುಡುಕುತ್ತಿದ್ದೀರಾ?",
        "ನಿಮ್ಮ ಐಶಾರಾಮಿ ಆಸ್ತಿಯ ಮೌಲ್ಯ ಎಷ್ಟು?",
        "ನಿಮ್ಮ ಒಟ್ಟು ಬ್ಯಾಂಕ್ ಆಸ್ತಿಯ ಮೌಲ್ಯ ಎಷ್ಟು?"
    ],
    "ml-IN": [
        "നിങ്ങൾക്ക് എത്ര ആശ്രിതർ ഉണ്ട്?",
        "നിങ്ങൾക്ക് എത്ര മാസത്തേക്ക് ലോൺ വേണം?",
        "നിങ്ങൾ ഒരു ബിരുദധാരിയാണോ അല്ലാത്തതാണോ?",
        "നിങ്ങളുടെ വാർഷിക വരുമാനം എത്ര?",
        "നിങ്ങളുടെ താമസ ആസ്തിയുടെ മൂല്യം എത്ര?",
        "നിങ്ങളുടെ വ്യാപാര ആസ്തിയുടെ മൂല്യം എത്ര?",
        "നിങ്ങൾ സ്വയംതൊഴിലാളിയാണോ?",
        "നിങ്ങൾക്ക് എത്രത്തോളം ലോൺ ആവശ്യമാണ്?",
        "നിങ്ങൾ ഏത് തരത്തിലുള്ള ലോൺ തിരയുകയാണോ?",
        "നിങ്ങളുടെ ആഡംബര ആസ്തിയുടെ മൂല്യം എത്ര?",
        "നിങ്ങളുടെ മൊത്തം ബാങ്ക് ആസ്തിയുടെ മൂല്യം എത്ര?"
    ],
    "mr-IN": [
        "तुमच्याकडे किती अवलंबित आहेत?",
        "तुम्हाला किती महिन्यांसाठी कर्ज पाहिजे?",
        "तुम्ही पदवीधर आहात का?",
        "तुमचे वार्षिक उत्पन्न किती आहे?",
        "तुमच्या निवासी मालमत्तेचे मूल्य किती आहे?",
        "तुमच्या व्यावसायिक मालमत्तेचे मूल्य किती आहे?",
        "तुम्ही स्वयंरोजगार आहात का?",
        "तुम्हाला किती कर्ज रक्कम हवी आहे?",
        "तुम्ही कोणत्या प्रकारचे कर्ज शोधत आहात?",
        "तुमच्या लक्झरी मालमत्तेचे मूल्य किती आहे?",
        "तुमच्या एकूण बँक मालमत्तेचे मूल्य किती आहे?"
    ],
    "od-IN": [
        "ଆପଣଙ୍କ ନିର୍ଭରକ କିଏ?",
        "ଆପଣ କେତେ ମାସ ପାଇଁ ଋଣ ଚାହୁଁଛନ୍ତି?",
        "ଆପଣ ସ୍ନାତକ କି ନୁହଁ?",
        "ଆପଣଙ୍କ ବାର୍ଷିକ ଆୟ କେତେ?",
        "ଆପଣଙ୍କ ନିବାସ ସମ୍ପତ୍ତିର ମୂଲ୍ୟ କେତେ?",
        "ଆପଣଙ୍କ ବାଣିଜ୍ୟିକ ସମ୍ପତ୍ତିର ମୂଲ୍ୟ କେତେ?",
        "ଆପଣ କି ସ୍ୱୟଂରୋଜଗାରୀ?",
        "ଆପଣଙ୍କୁ କେତେ ରିଣ ରାଶି ଦରକାର?",
        "ଆପଣ କେଉଁ ପ୍ରକାରର ଋଣ ଦେଖୁଛନ୍ତି?",
        "ଆପଣଙ୍କ ବିଲାସୀ ସମ୍ପତ୍ତିର ମୂଲ୍ୟ କେତେ?",
        "ଆପଣଙ୍କ ମୋଟ ବ୍ୟାଙ୍କ ସମ୍ପତ୍ତିର ମୂଲ୍ୟ କେତେ?"
    ],
    "pa-IN": [
        "ਤੁਹਾਡੇ ਉੱਤੇ ਕਿੰਨੇ ਨਿਰਭਰ ਕਰਦੇ ਹਨ?",
        "ਤੁਸੀਂ ਕਿੰਨੇ ਮਹੀਨਿਆਂ ਲਈ ਕਰਜ਼ਾ ਚਾਹੁੰਦੇ ਹੋ?",
        "ਕੀ ਤੁਸੀਂ ਗ੍ਰੈਜੁਏਟ ਹੋ ਜਾਂ ਨਾ-ਗ੍ਰੈਜੁਏਟ?",
        "ਤੁਹਾਡੀ ਸਾਲਾਨਾ ਆਮਦਨ ਕਿੰਨੀ ਹੈ?",
        "ਤੁਹਾਡੀ ਰਿਹਾਇਸ਼ੀ ਸੰਪਤੀ ਦੀ ਕੀਮਤ ਕੀ ਹੈ?",
        "ਤੁਹਾਡੀ ਵਪਾਰਕ ਸੰਪਤੀ ਦੀ ਕੀਮਤ ਕੀ ਹੈ?",
        "ਕੀ ਤੁਸੀਂ ਸਵੈ-ਰੋਜ਼ਗਾਰ ਹੋ?",
        "ਤੁਹਾਨੂੰ ਕਿੰਨੀ ਕਰਜ਼ਾ ਰਕਮ ਦੀ ਲੋੜ ਹੈ?",
        "ਤੁਸੀਂ ਕਿਸ ਤਰ੍ਹਾਂ ਦਾ ਕਰਜ਼ਾ ਲੈਣਾ ਚਾਹੁੰਦੇ ਹੋ?",
        "ਤੁਹਾਡੀ ਵਿਲਾਸੀ ਸੰਪਤੀ ਦੀ ਕੀਮਤ ਕੀ ਹੈ?",
        "ਤੁਹਾਡੀ ਕੁੱਲ ਬੈਂਕ ਸੰਪਤੀ ਦੀ ਕੀਮਤ ਕੀ ਹੈ?"
    ],
    "ta-IN": [
        "உங்களிடம் எத்தனை phụவலங்கர்கள் உள்ளனர்?",
        "நீங்கள் எத்தனை மாதத்திற்கு கடன் தேவை?",
        "நீங்கள் ஒரு பட்டதாரியா அல்லது பட்டமில்லாதவரா?",
        "உங்கள் ஆண்டு வருமானம் என்ன?",
        "உங்கள் குடியிருப்பு சொத்தின் மதிப்பு என்ன?",
        "உங்கள் வணிக சொத்தின் மதிப்பு என்ன?",
        "நீங்கள் சுய தொழிலாளியா?",
        "நீங்கள் எவ்வளவு கடன் தேவை?",
        "நீங்கள் எந்த வகையான கடன் தேடுகிறீர்கள்?",
        "உங்கள் ஆடம்பர சொத்தின் மதிப்பு என்ன?",
        "உங்கள் மொத்த வங்கி சொத்தின் மதிப்பு என்ன?"
    ],
    "te-IN": [
        "మీకు ఎంత మంది ఆధారపడిన వారు ఉన్నారు?",
        "మీకు ఎన్ని నెలలు రుణం అవసరం?",
        "మీరు గ్రాడ్యుయేట్ లేక నాన్-గ్రాడ్యుయేట్?",
        "మీ వార్షిక ఆదాయం ఎంత?",
        "మీ నివాస ఆస్తి విలువ ఎంత?",
        "మీ వాణిజ్య ఆస్తి విలువ ఎంత?",
        "మీరు స్వయం ఉపాధిలో ఉన్నారా?",
        "మీకు ఎంత రుణ రాశి అవసరం?",
        "మీరు ఎలాంటి రుణం వెతుకుతున్నారు?",
        "మీ లగ్జరీ ఆస్తుల విలువ ఎంత?",
        "మీ మొత్తం బ్యాంక్ ఆస్తి విలువ ఎంత?"
    ]
}

# Store user session data
user_sessions = {}

def chunk_text(text, max_length=1000):
    """
    Split text into chunks of at most max_length characters 
    while preserving word boundaries.
    """
    chunks = []
    
    while len(text) > max_length:
        # Find the last space within the max length
        split_index = text.rfind(" ", 0, max_length)
        
        # If no space found, force split at max_length
        if split_index == -1:
            split_index = max_length
        
        # Add chunk and remove leading/trailing spaces
        chunks.append(text[:split_index].strip())
        text = text[split_index:].lstrip()
    
    # Add the last chunk if any text remains
    if text:
        chunks.append(text.strip())
    
    return chunks

def translate_with_sarvam(input_text, source_language, target_language):
    """
    Translate text using Sarvam Translation API with comprehensive chunk handling
    """
    if not SARVAM_API_KEY:
        print("Sarvam API key not available, falling back to Gemini translation")
        return translate_with_gemini(input_text, source_language, target_language)
    
    url = "https://api.sarvam.ai/translate"

    # Validate input parameters
    valid_languages = ["en-IN", "hi-IN", "bn-IN", "gu-IN", "kn-IN", "ml-IN", "mr-IN", "od-IN", "pa-IN", "ta-IN", "te-IN"]
    if source_language not in valid_languages or target_language not in valid_languages:
        print(f"Invalid language code for Sarvam API. Source: {source_language}, Target: {target_language}")
        return translate_with_gemini(input_text, source_language, target_language)

    # Chunk the text
    text_chunks = chunk_text(input_text)
    translated_chunks = []

    for chunk in text_chunks:
        payload = {
            "input": chunk,
            "source_language_code": source_language,
            "target_language_code": target_language,
            "speaker_gender": "Female",
            "mode": "formal",
            "enable_preprocessing": False,
            "output_script": None,
            "numerals_format": "international"
        }

        headers = {
            "Content-Type": "application/json",
            "api-subscription-key": SARVAM_API_KEY
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            # Check for HTTP errors
            response.raise_for_status()
            
            response_data = response.json()
            
            # Validate response
            if "translated_text" in response_data:
                translated_chunks.append(response_data["translated_text"])
                print(f"✅ Sarvam translation successful for chunk")
            else:
                print(f"⚠️ Unexpected Sarvam response: {response_data}")
                # Fallback to Gemini for this chunk
                fallback_translation = translate_with_gemini(chunk, source_language, target_language)
                translated_chunks.append(fallback_translation)
        
        except requests.exceptions.RequestException as req_err:
            print(f"❌ Sarvam API request error: {req_err}")
            # Fallback to Gemini for this chunk
            fallback_translation = translate_with_gemini(chunk, source_language, target_language)
            translated_chunks.append(fallback_translation)
        except ValueError as val_err:
            print(f"❌ Sarvam JSON parsing error: {val_err}")
            # Fallback to Gemini for this chunk
            fallback_translation = translate_with_gemini(chunk, source_language, target_language)
            translated_chunks.append(fallback_translation)
        except Exception as e:
            print(f"❌ Unexpected Sarvam error: {e}")
            # Fallback to Gemini for this chunk
            fallback_translation = translate_with_gemini(chunk, source_language, target_language)
            translated_chunks.append(fallback_translation)

    # Combine translated chunks
    final_translation = " ".join(translated_chunks)
    return final_translation

def translate_with_gemini(input_text, source_language, target_language):
    """
    Fallback translation using Gemini API
    """
    if not model:
        return input_text
    
    try:
        source_name = LANGUAGES.get(source_language, 'English')
        target_name = LANGUAGES.get(target_language, 'English')
        
        prompt = f"""
        Translate the following text from {source_name} to {target_name}:
        "{input_text}"
        
        Provide only the translation without any additional text.
        """
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        return response.text.strip()
    except Exception as e:
        print(f"❌ Gemini translation error: {e}")
        return input_text

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "gemini_api": "available" if model else "unavailable",
        "sarvam_api": "available" if SARVAM_API_KEY else "unavailable",
        "translation_mode": "sarvam_primary" if SARVAM_API_KEY else "gemini_only"
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.json
        message = data.get('message', '')
        language_code = data.get('languageCode', 'en-IN')
        user_id = data.get('userId', str(uuid.uuid4()))
        is_greeting = data.get('isGreeting', False)
        
        if is_greeting:
            # Return initial greeting
            greeting = get_greeting_message(language_code)
            return jsonify({
                "response": greeting,
                "success": True
            })
        
        # Generate AI response using Gemini
        if model:
            # Create context-aware prompt
            prompt = f"""
            You are CrediBot, a helpful multilingual assistant specializing in loan and financial guidance.
            User's language: {LANGUAGES.get(language_code, 'English')}
            User's message: {message}
            
            Provide a helpful, professional response about loans, financial guidance, or general assistance.
            Be concise but informative. If it's about loans, provide practical advice.
            Use plain text format without any special formatting.
            """
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            bot_response = response.text
            
            # Translate response to user's language using Sarvam API
            if language_code != "en-IN":
                bot_response = translate_with_sarvam(bot_response, "en-IN", language_code)
            
        else:
            # Fallback response
            bot_response = get_fallback_response(message, language_code)
        
        return jsonify({
            "response": bot_response,
            "success": True
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            "response": "I apologize, but I'm experiencing technical difficulties. Please try again.",
            "success": False,
            "error": str(e)
        }), 500

@app.route('/translate', methods=['POST'])
def translate():
    """Translation endpoint using Sarvam API with Gemini fallback"""
    try:
        data = request.json
        input_text = data.get('input', '')
        source_lang = data.get('source_language_code', 'en-IN')
        target_lang = data.get('target_language_code', 'en-IN')
        
        if source_lang == target_lang:
            return jsonify({
                "translated_text": input_text,
                "success": True,
                "translation_service": "none_required"
            })
        
        # Use Sarvam API for translation with Gemini fallback
        translated_text = translate_with_sarvam(input_text, source_lang, target_lang)
        
        return jsonify({
            "translated_text": translated_text,
            "success": True,
            "translation_service": "sarvam_primary"
        })
        
    except Exception as e:
        return jsonify({
            "translated_text": data.get('input', ''),
            "success": False,
            "error": str(e)
        }), 500

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    """Text-to-speech endpoint (mock implementation)"""
    try:
        data = request.json
        inputs = data.get('inputs', [])
        target_language = data.get('target_language_code', 'en-IN')
        
        # For now, return a simple success response
        # In production, you would integrate with a TTS service like Sarvam AI TTS
        return jsonify({
            "success": True,
            "message": "TTS service available - integrate Sarvam AI TTS for production"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    """Speech-to-text endpoint (mock implementation)"""
    try:
        # For now, return a mock transcription
        # In production, you would integrate with Sarvam AI STT service
        return jsonify({
            "transcription": "This is a mock transcription - integrate Sarvam AI STT for production",
            "success": True
        })
        
    except Exception as e:
        return jsonify({
            "transcription": "",
            "success": False,
            "error": str(e)
        }), 500

@app.route('/read-document', methods=['POST'])
def read_document():
    """Document processing endpoint"""
    try:
        data = request.json
        document_text = data.get('documentText', '')
        language_code = data.get('languageCode', 'en-IN')
        file_type = data.get('fileType', 'text')
        
        if model:
            language_name = LANGUAGES.get(language_code, 'English')
            
            prompt = f"""
            You are a loan document expert. Analyze the following document content and provide 
            a clear explanation about:
            1. What type of document this is
            2. Key information contained in the document
            3. How this document relates to loan applications
            4. Any important details the user should understand
            
            Document content: {document_text}
            
            Provide a helpful, easy-to-understand explanation in plain text format.
            """
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            explanation = response.text
            
            # Translate to user's language if needed
            if language_code != "en-IN":
                explanation = translate_with_sarvam(explanation, "en-IN", language_code)
            
        else:
            explanation = f"Document processed. This appears to be a loan-related document. Please review the contents carefully and ensure all information is accurate."
        
        return jsonify({
            "vernacular_explanation": explanation,
            "success": True
        })
        
    except Exception as e:
        return jsonify({
            "vernacular_explanation": "Error processing document",
            "success": False,
            "error": str(e)
        }), 500

@app.route('/set-language', methods=['POST'])
def set_language():
    """Set user language preference"""
    try:
        data = request.json
        language_code = data.get('language_code', 'en-IN')
        
        return jsonify({
            "success": True,
            "language": language_code,
            "message": f"Language set to {LANGUAGES.get(language_code, 'English')}"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Loan-specific endpoints with enhanced translation
@app.route('/loan/start-questions', methods=['POST'])
def start_loan_questions():
    """Start loan eligibility questionnaire"""
    try:
        data = request.json
        user_id = data.get('userId', str(uuid.uuid4()))
        language_code = data.get('languageCode', 'en-IN')
        
        # Get questions for the language
        questions = LOAN_QUESTIONS.get(language_code, LOAN_QUESTIONS['en-IN'])
        shuffled_questions = questions.copy()
        random.shuffle(shuffled_questions)
        
        # Store session data
        user_sessions[user_id] = {
            "questions": shuffled_questions,
            "answers": {},
            "current_question": 0,
            "language_code": language_code
        }
        
        return jsonify({
            "question": {
                "question": shuffled_questions[0],
                "questionIndex": 0,
                "totalQuestions": len(shuffled_questions),
                "languageCode": language_code
            },
            "isComplete": False,
            "success": True
        })
        
    except Exception as e:
        return jsonify({
            "question": None,
            "isComplete": False,
            "success": False,
            "error": str(e)
        }), 500

@app.route('/loan/answer', methods=['POST'])
def submit_loan_answer():
    """Submit answer to loan question"""
    try:
        data = request.json
        user_id = data.get('userId')
        answer = data.get('answer')
        question_index = data.get('questionIndex')
        
        if user_id not in user_sessions:
            return jsonify({
                "question": None,
                "isComplete": False,
                "success": False,
                "error": "Session not found"
            }), 404
        
        session = user_sessions[user_id]
        questions = session['questions']
        
        # Store the answer
        session['answers'][questions[question_index]] = answer
        
        # Check if more questions remain
        next_question_index = question_index + 1
        if next_question_index < len(questions):
            session['current_question'] = next_question_index
            return jsonify({
                "question": {
                    "question": questions[next_question_index],
                    "questionIndex": next_question_index,
                    "totalQuestions": len(questions),
                    "languageCode": session['language_code']
                },
                "isComplete": False,
                "success": True
            })
        else:
            # All questions answered
            return jsonify({
                "question": None,
                "isComplete": True,
                "success": True
            })
        
    except Exception as e:
        return jsonify({
            "question": None,
            "isComplete": False,
            "success": False,
            "error": str(e)
        }), 500

@app.route('/loan/check-eligibility', methods=['POST'])
def check_loan_eligibility():
    """Check loan eligibility based on answers with enhanced translation"""
    try:
        data = request.json
        user_id = data.get('userId')
        
        if user_id not in user_sessions:
            return jsonify({
                "eligibilityResult": "Session not found",
                "isEligible": False,
                "recommendations": [],
                "requiredDocuments": [],
                "success": False,
                "error": "Session not found"
            }), 404
        
        session = user_sessions[user_id]
        answers = session['answers']
        language_code = session['language_code']
        language_name = LANGUAGES.get(language_code, 'English')
        
        if model:
            # Create detailed prompt for loan eligibility (same as bot1.py)
            answers_text = "\n".join([f"- {q}: {a}" for q, a in answers.items()])
            
            prompt = f"""
            Act as a professional Indian bank loan advisor. Analyze the following financial details 
            and provide a comprehensive loan eligibility assessment with specific, structured advice:

            Financial Profile:
            {answers_text}

            Provide a response with the following structure:
            A. Loan Eligibility Assessment
            - Clearly state if the loan is approved or not
            - Provide specific reasons for the decision

            B. If Loan is Eligible:
            1. Detailed Bank Loan Acquisition Steps (Indian Banking Context)
            - Step-by-step process to apply for the loan
            - Recommended bank procedures
            - Expected timeline

            2. Required Documentation
            - Comprehensive list of documents needed
            - Specific Indian banking document requirements
            - Tips for document preparation

            3. Professional Recommendations
            - Tailored financial advice
            - Suggestions for loan optimization
            - Long-term financial planning insights

            C. If Loan is Not Eligible:
            1. Specific Reasons for Rejection
            - Detailed explanation of why the loan was not approved

            2. Actionable Improvement Strategies
            - Concrete steps to improve loan eligibility
            - Financial health improvement suggestions
            - Specific recommendations for increasing creditworthiness

            3. Alternative Financial Guidance
            - Alternative financing options
            - Steps to strengthen financial profile
            - Professional advice for future loan applications

            Ensure the advice is:
            - Practical and actionable
            - Specific to Indian banking context
            - Professionally and empathetically worded
            - Use plain text format without any special formatting
            """
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            eligibility_result = response.text
            
            # Translate to user's language using Sarvam API
            if language_code != "en-IN":
                eligibility_result = translate_with_sarvam(eligibility_result, "en-IN", language_code)
            
            # Determine eligibility from response (simple keyword check)
            is_eligible = "approved" in eligibility_result.lower() or "eligible" in eligibility_result.lower()
            
            # Generate recommendations in user's language
            basic_recommendations = [
                "Maintain a good credit score",
                "Ensure all documents are up to date",
                "Consider a co-applicant if needed",
                "Compare interest rates from different banks"
            ]
            
            basic_documents = [
                "Identity Proof (Aadhar Card/PAN Card)",
                "Address Proof (Utility Bills/Rent Agreement)",
                "Income Proof (Salary Slips/ITR)",
                "Bank Statements (6 months)",
                "Employment Certificate"
            ]
            
            # Translate recommendations and documents if needed
            if language_code != "en-IN":
                recommendations = []
                for rec in basic_recommendations:
                    translated_rec = translate_with_sarvam(rec, "en-IN", language_code)
                    recommendations.append(translated_rec)
                
                required_documents = []
                for doc in basic_documents:
                    translated_doc = translate_with_sarvam(doc, "en-IN", language_code)
                    required_documents.append(translated_doc)
            else:
                recommendations = basic_recommendations
                required_documents = basic_documents
            
        else:
            eligibility_result = "Unable to process loan application due to technical issues. Please contact support."
            is_eligible = False
            recommendations = []
            required_documents = []
        
        # Clean up session
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        return jsonify({
            "eligibilityResult": eligibility_result,
            "isEligible": is_eligible,
            "recommendations": recommendations,
            "requiredDocuments": required_documents,
            "success": True,
            "translationService": "sarvam" if SARVAM_API_KEY else "gemini"
        })
        
    except Exception as e:
        return jsonify({
            "eligibilityResult": "Error processing eligibility check",
            "isEligible": False,
            "recommendations": [],
            "requiredDocuments": [],
            "success": False,
            "error": str(e)
        }), 500

def get_greeting_message(language_code):
    """Get greeting message based on language"""
    greetings = {
        "en-IN": "Hello! I'm CrediBot, your multilingual loan assistant. How can I help you with your financial queries today?",
        "hi-IN": "नमस्ते! मैं क्रेडिबॉट हूँ, आपका बहुभाषी ऋण सहायक। आज मैं आपकी वित्तीय जरूरतों में कैसे मदद कर सकता हूँ?",
        "ta-IN": "வணக்கம்! நான் கிரெடிபாட், உங்கள் பலமொழி கடன் உதவியாளர். இன்று உங்கள் நிதிக் கேள்விகளில் நான் எப்படி உதவ முடியும்?",
        "te-IN": "నమస్కారం! నేను క్రెడిబాట్, మీ బహుభాషా రుణ సహాయకుడు. ఈ రోజు మీ ఆర్థిక ప్రశ్నలలో నేను ఎలా సహాయం చేయగలను?",
        "kn-IN": "ನಮಸ್ಕಾರ! ನಾನು ಕ್ರೆಡಿಬಾಟ್, ನಿಮ್ಮ ಬಹುಭಾಷಾ ಸಾಲ ಸಹಾಯಕ. ಇಂದು ನಿಮ್ಮ ಹಣಕಾಸಿನ ಪ್ರಶ್ನೆಗಳಲ್ಲಿ ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
        "ml-IN": "നമസ്കാരം! ഞാൻ ക്രെഡിബോട്ട്, നിങ്ങളുടെ ബഹുഭാഷാ വായ്പാ സഹായി. ഇന്ന് നിങ്ങളുടെ സാമ്പത്തിക ചോദ്യങ്ങളിൽ എനിക്ക് എങ്ങനെ സഹായിക്കാം?"
    }
    return greetings.get(language_code, greetings["en-IN"])

def get_fallback_response(message, language_code):
    """Get fallback response when AI is not available"""
    fallbacks = {
        "en-IN": "Thank you for your message. I'm here to help with loan and financial guidance. Please let me know what specific information you need.",
        "hi-IN": "आपके संदेश के लिए धन्यवाद। मैं ऋण और वित्तीय मार्गदर्शन में आपकी सहायता के लिए यहाँ हूँ।",
        "ta-IN": "உங்கள் செய்திக்கு நன்றி. கடன் மற்றும் நிதி வழிகாட்டுதலில் உதவ நான் இங்கே இருக்கிறேன்.",
        "te-IN": "మీ సందేశానికి ధన్యవాదాలు. రుణ మరియు ఆర్థిక మార్గదర్శకత్వంలో సహాయం చేయడానికి నేను ఇక్కడ ఉన్నాను।",
        "kn-IN": "ನಿಮ್ಮ ಸಂದೇಶಕ್ಕೆ ಧನ್ಯವಾದಗಳು. ಸಾಲ ಮತ್ತು ಹಣಕಾಸಿನ ಮಾರ್ಗದರ್ಶನದಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ನಾನು ಇಲ್ಲಿದ್ದೇನೆ।",
        "ml-IN": "നിങ്ങളുടെ സന്ദേശത്തിന് നന്ദി. വായ്പയും സാമ്പത്തിക മാർഗ്ഗനിർദ്ദേശവും സഹായിക്കാൻ ഞാൻ ഇവിടെയുണ്ട്।"
    }
    return fallbacks.get(language_code, fallbacks["en-IN"])

if __name__ == '__main__':
    print("🚀 Starting CrediBot Enhanced Flask API Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("🔧 Features:")
    print("   ✅ Sarvam AI Translation API integration")
    print("   ✅ Gemini AI for chat responses")
    print("   ✅ Complete multilingual loan eligibility assessment")
    print("   ✅ Professional translation with fallback support")
    print("🔧 Make sure to update your Android app's BASE_URL accordingly")
    app.run(host='0.0.0.0', port=8000, debug=True)
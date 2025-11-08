import os
import random
import uuid
import base64
import asyncio
import requests
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import google.generativeai as genai
from werkzeug.utils import secure_filename
from PIL import Image
import io
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# API Keys - In production, use environment variables
TOKEN = "8125759209:AAEWipIexhQeHmIFykw1J3xpG6ujZPRhIyM"
GEMINI_API_KEY = "AIzaSyC9i96-x18BGKIeV7HOHKn-piu4e5R9IUs"
SARVAM_API_KEY = "d60e2e18-3b3c-492d-8faf-7f9db7c55201"

# Configure Gemini API
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    logger.info("Gemini API initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini client: {e}")
    model = None

# Supported Languages
LANGUAGES = {
    "English": "en-IN", "हिंदी": "hi-IN", "বাংলা": "bn-IN", "ગુજરાતી": "gu-IN",
    "ಕನ್ನಡ": "kn-IN", "മലയാളം": "ml-IN", "मराठी": "mr-IN", "ଓଡିଆ": "od-IN",
    "ਪੰਜਾਬੀ": "pa-IN", "தமிழ்": "ta-IN", "తెలుగు": "te-IN"
}

# Loan questions in all languages (from bot2.py)
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
        "உங்களிடம் எத்தனை ஆதாரங்கள் உள்ளனர்?",
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
        "మీకు ఎంతమంది ఆధారపడిన వారు ఉన్నారు?",
        "మీకు ఎన్ని నెలలపాటు రుణం అవసరం?",
        "మీరు గ్రాడ్యుయేట్ లేదా నాన్-గ్రాడ్యుయేట్?",
        "మీ వార్షిక ఆదాయం ఎంత?",
        "మీ నివాస ఆస్తుల విలువ ఎంత?",
        "మీ వాణిజ్య ఆస్తుల విలువ ఎంత?",
        "మీరు స్వయం ఉపాధిలో ఉన్నారా?",
        "మీకు ఎంత రుణ మొత్తం అవసరం?",
        "మీరు ఎలాంటి రుణం వెతుకుతున్నారు?",
        "మీ లగ్జరీ ఆస్తుల విలువ ఎంత?",
        "మీ మొత్తం బ్యాంక్ ఆస్తుల విలువ ఎంత?"
    ]
}

# Global session storage
user_sessions = {}

def chunk_text(text, max_length=1000):
    """Split text into chunks while preserving word boundaries."""
    chunks = []
    while len(text) > max_length:
        split_index = text.rfind(" ", 0, max_length)
        if split_index == -1:
            split_index = max_length
        chunks.append(text[:split_index].strip())
        text = text[split_index:].lstrip()
    if text:
        chunks.append(text.strip())
    return chunks

def translate_text(input_text, source_language, target_language):
    """Translate text using Sarvam Translation API."""
    if source_language == target_language:
        return input_text
        
    url = "https://api.sarvam.ai/translate"
    valid_languages = ["en-IN", "hi-IN", "bn-IN", "gu-IN", "kn-IN", "ml-IN", "mr-IN", "od-IN", "pa-IN", "ta-IN", "te-IN"]
    
    if source_language not in valid_languages or target_language not in valid_languages:
        logger.warning(f"Invalid language codes: {source_language} -> {target_language}")
        return input_text

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
            response.raise_for_status()
            response_data = response.json()
            
            if "translated_text" in response_data:
                translated_chunks.append(response_data["translated_text"])
            else:
                translated_chunks.append(chunk)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            translated_chunks.append(chunk)

    return " ".join(translated_chunks)

def text_to_speech(text, target_language, speaker=None):
    """Convert text to speech using Sarvam AI TTS API."""
    url = "https://api.sarvam.ai/text-to-speech"
    
    # Default speaker mapping based on language
    default_speakers = {
        "hi-IN": "meera",
        "bn-IN": "tavithra", 
        "gu-IN": "maitreyi",
        "kn-IN": "arvind",
        "ml-IN": "amol",
        "mr-IN": "amartya",
        "od-IN": "diya",
        "pa-IN": "neel",
        "ta-IN": "misha",
        "te-IN": "vian",
        "en-IN": "arjun"
    }
    
    chosen_speaker = speaker or default_speakers.get(target_language, "meera")
    text = text[:500]  # Truncate to API limits
    
    payload = {
        "inputs": [text],
        "target_language_code": target_language,
        "speaker": chosen_speaker,
        "pitch": 0,
        "pace": 1.0,
        "loudness": 1.0,
        "speech_sample_rate": 22050,
        "enable_preprocessing": True,
        "model": "bulbul:v1"
    }
    
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        response_data = response.json()
        
        if response_data.get("audios"):
            return response_data["audios"][0]
        return None
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "gemini_available": model is not None,
        "sarvam_available": bool(SARVAM_API_KEY)
    })

@app.route('/set-language', methods=['POST'])
def set_language():
    """Set user's preferred language."""
    try:
        data = request.get_json()
        session_id = data.get('session_id', str(uuid.uuid4()))
        language_code = data.get('language_code', 'en-IN')
        
        if session_id not in user_sessions:
            user_sessions[session_id] = {}
            
        user_sessions[session_id]['language'] = language_code
        logger.info(f"Language set to {language_code} for session {session_id}")
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "language_code": language_code,
            "message": f"Language set to {language_code}"
        })
    except Exception as e:
        logger.error(f"Set language error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/translate', methods=['POST'])
def translate():
    """Translate text between languages."""
    try:
        data = request.get_json()
        input_text = data.get('input', '')
        source_language_code = data.get('source_language_code', 'en-IN')
        target_language_code = data.get('target_language_code', 'en-IN')
        
        if not input_text:
            return jsonify({"error": "No input text provided"}), 400
            
        translated_text = translate_text(input_text, source_language_code, target_language_code)
        
        return jsonify({
            "translated_text": translated_text,
            "source_language": source_language_code,
            "target_language": target_language_code
        })
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech_endpoint():
    """Convert text to speech."""
    try:
        data = request.get_json()
        inputs = data.get('inputs', [])
        target_language_code = data.get('target_language_code', 'en-IN')
        speaker = data.get('speaker')
        
        if not inputs:
            return jsonify({"error": "No input text provided"}), 400
            
        # Process first input text
        text = inputs[0]
        audio_base64 = text_to_speech(text, target_language_code, speaker)
        
        if audio_base64:
            # Decode base64 to binary audio data
            audio_bytes = base64.b64decode(audio_base64)
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_file.write(audio_bytes)
            temp_file.close()
            
            return send_file(temp_file.name, mimetype='audio/wav', as_attachment=False)
        else:
            return jsonify({"error": "Failed to generate audio"}), 500
            
    except Exception as e:
        logger.error(f"TTS endpoint error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle general chat messages."""
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        language_code = data.get('language_code', 'en-IN')
        is_greeting = data.get('isGreeting', False)
        
        if session_id not in user_sessions:
            user_sessions[session_id] = {'language': language_code}
        
        # Handle initial greeting
        if is_greeting or message == "initial_greeting":
            greeting = "Hello! I'm CrediBot, your multilingual loan advisor. I can help you check loan eligibility, understand banking procedures, and provide financial guidance in your preferred language. How can I assist you today?"
            
            return jsonify({
                "response": greeting,
                "session_id": session_id,
                "language": language_code
            })
        
        # Generate AI response using Gemini
        if model:
            prompt = f"""
            You are CrediBot, a professional Indian banking and loan advisor assistant. 
            Respond to the user's query about loans, banking, or financial advice in a helpful, 
            accurate, and professional manner. Keep responses concise but informative.
            
            User query: {message}
            
            Provide practical advice specific to Indian banking context.
            """
            
            try:
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 1,
                        "top_k": 1,
                        "max_output_tokens": 512
                    }
                )
                bot_response = response.text
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                bot_response = "I apologize, but I'm having trouble processing your request right now. Please try again later."
        else:
            bot_response = "I'm here to help with your loan and banking questions. Please ask me anything about loan eligibility, documentation, or financial advice."
        
        return jsonify({
            "response": bot_response,
            "session_id": session_id,
            "language": language_code
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/loan/start-questions', methods=['POST'])
def start_loan_questions():
    """Start the loan eligibility questionnaire."""
    try:
        data = request.get_json()
        session_id = data.get('session_id', str(uuid.uuid4()))
        language_code = data.get('language_code', 'en-IN')
        
        # Initialize session
        if session_id not in user_sessions:
            user_sessions[session_id] = {}
        
        # Get questions for the language
        questions = LOAN_QUESTIONS.get(language_code, LOAN_QUESTIONS["en-IN"]).copy()
        random.shuffle(questions)
        
        user_sessions[session_id].update({
            'language': language_code,
            'questions': questions,
            'current_question': 0,
            'responses': {},
            'state': 'asking_questions'
        })
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "first_question": questions[0],
            "total_questions": len(questions),
            "current_question_number": 1
        })
        
    except Exception as e:
        logger.error(f"Start loan questions error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/loan/answer', methods=['POST'])
def submit_loan_answer():
    """Submit answer to current loan question."""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        answer = data.get('answer', '')
        
        if not session_id or session_id not in user_sessions:
            return jsonify({"error": "Invalid session"}), 400
        
        session = user_sessions[session_id]
        questions = session.get('questions', [])
        current_q = session.get('current_question', 0)
        responses = session.get('responses', {})
        
        # Store current answer
        if current_q < len(questions):
            responses[questions[current_q]] = answer
            session['responses'] = responses
            session['current_question'] = current_q + 1
            
            # Check if more questions remain
            if current_q + 1 < len(questions):
                next_question = questions[current_q + 1]
                return jsonify({
                    "has_next_question": True,
                    "next_question": next_question,
                    "current_question_number": current_q + 2,
                    "total_questions": len(questions)
                })
            else:
                # All questions answered
                session['state'] = 'questions_completed'
                return jsonify({
                    "has_next_question": False,
                    "message": "All questions completed. Processing loan eligibility...",
                    "ready_for_eligibility": True
                })
        
        return jsonify({"error": "Invalid question state"}), 400
        
    except Exception as e:
        logger.error(f"Submit answer error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/loan/check-eligibility', methods=['POST'])
def check_loan_eligibility():
    """Check loan eligibility based on submitted answers."""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id or session_id not in user_sessions:
            return jsonify({"error": "Invalid session"}), 400
        
        session = user_sessions[session_id]
        responses = session.get('responses', {})
        language_code = session.get('language', 'en-IN')
        
        if not responses:
            return jsonify({"error": "No responses found"}), 400
        
        # Generate eligibility assessment using Gemini
        if model:
            prompt = f"""
            Act as a professional Indian bank loan advisor. Analyze the following financial details 
            and provide a comprehensive loan eligibility assessment with specific, structured advice:

            Financial Profile:
            {chr(10).join(f"- {key}: {value}" for key, value in responses.items())}

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
            - Use plain text format without special formatting
            """
            
            try:
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 1,
                        "top_k": 1,
                        "max_output_tokens": 1024
                    }
                )
                eligibility_result = response.text
                
                # Translate to user's language if needed
                if language_code != "en-IN":
                    eligibility_result = translate_text(
                        eligibility_result, 
                        "en-IN", 
                        language_code
                    )
                
                # Mark session as completed
                session['state'] = 'completed'
                session['last_result'] = eligibility_result
                
                return jsonify({
                    "success": True,
                    "eligibility_result": eligibility_result,
                    "language": language_code
                })
                
            except Exception as e:
                logger.error(f"Gemini API error in eligibility check: {e}")
                return jsonify({"error": "Failed to generate eligibility assessment"}), 500
        else:
            return jsonify({"error": "AI model not available"}), 500
            
    except Exception as e:
        logger.error(f"Check eligibility error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/read-document', methods=['POST'])
def read_document():
    """Process uploaded document and provide vernacular explanation."""
    try:
        if 'document' not in request.files:
            return jsonify({"error": "No document uploaded"}), 400
        
        file = request.files['document']
        language_code = request.form.get('language_code', 'en-IN')
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Simple document processing simulation
        document_analysis = """
        This appears to be a loan agreement document. Based on the content, here are the key points:
        
        1. Loan Amount: As specified in the document
        2. Interest Rate: Please verify the annual percentage rate
        3. Repayment Terms: Check the monthly installment amount and tenure
        4. Important Clauses: Review all terms and conditions carefully
        5. Required Actions: Ensure all signatures and documentation are complete
        
        Please review all terms carefully before signing. If you have questions about any clause, 
        consult with a financial advisor or the bank representative.
        """
        
        # Translate to requested language
        if language_code != "en-IN":
            document_analysis = translate_text(
                document_analysis,
                "en-IN",
                language_code
            )
        
        return jsonify({
            "success": True,
            "vernacular_explanation": document_analysis,
            "language": language_code
        })
        
    except Exception as e:
        logger.error(f"Document processing error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('audio', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    logger.info("Starting CrediBot Flask API Server...")
    logger.info(f"Gemini API Status: {'Available' if model else 'Not Available'}")
    logger.info(f"Sarvam API Status: {'Available' if SARVAM_API_KEY else 'Not Available'}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
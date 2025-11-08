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
import re
from io import BytesIO
from dotenv import load_dotenv
from groq import Groq

# OCR imports (Tesseract)
import pytesseract
from pdf2image import convert_from_bytes

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')
CORS(app)

# API Keys - Load from environment variables with correct defaults
SARVAM_API_KEY = os.getenv('SARVAM_API_KEY', 'sk_uttanwco_NUp2bWPxXWW3xhZiV0YXp6nE')  
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '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')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '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')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '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')

# Configure APIs
try:
    genai.configure(api_key='default_key')
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    logger.info("Gemini API initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini client: {e}")
    gemini_model = None

# Initialize Groq client (for advanced document processing)
groq_client = None
if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("Groq API initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {e}")

# DeepSeek integration via OpenRouter API (no special client needed)
deepseek_available = bool(DEEPSEEK_API_KEY)

# Tesseract configuration (adjust path as needed)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configuration
UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'audio'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# Supported Languages with proper display names
LANGUAGES = {
    "English": "en-IN",
    "हिंदी": "hi-IN",
    "বাংলা": "bn-IN",
    "ગુજરાતી": "gu-IN",
    "ಕನ್ನಡ": "kn-IN",
    "മലയാളം": "ml-IN",
    "मराठी": "mr-IN",
    "ଓଡିଆ": "od-IN",
    "ਪੰਜਾਬੀ": "pa-IN",
    "தமிழ்": "ta-IN",
    "తెలుగు": "te-IN"
}

# Language configuration for TTS
LANGUAGE_CONFIG = {
    'en-IN': {"model": "bulbul:v2", "chunk_size": 500, "silence_bytes": 2000, "speaker": "anushka"},
    'hi-IN': {"model": "bulbul:v2", "chunk_size": 300, "silence_bytes": 3000,
              "speaker": "abhilash"},
    'ta-IN': {"model": "bulbul:v2", "chunk_size": 300, "silence_bytes": 3000, "speaker": "vidya"},
    'te-IN': {"model": "bulbul:v2", "chunk_size": 300, "silence_bytes": 3000, "speaker": "teja"},
    'kn-IN': {"model": "bulbul:v2", "chunk_size": 300, "silence_bytes": 3000, "speaker": "kavya"},
    'ml-IN': {"model": "bulbul:v2", "chunk_size": 300, "silence_bytes": 3000, "speaker": "arya"},
    'mr-IN': {"model": "bulbul:v2", "chunk_size": 300, "silence_bytes": 3000, "speaker": "sakshi"},
    'bn-IN': {"model": "bulbul:v2", "chunk_size": 300, "silence_bytes": 3000, "speaker": "ishita"},
    'gu-IN': {"model": "bulbul:v2", "chunk_size": 300, "silence_bytes": 3000, "speaker": "kiran"},
    'pa-IN': {"model": "bulbul:v2", "chunk_size": 300, "silence_bytes": 3000, "speaker": "ranjit"},
    'od-IN': {"model": "bulbul:v2", "chunk_size": 300, "silence_bytes": 3000, "speaker": "anushka"}
    # Fallback speaker
}

# Loan questions in all languages (comprehensive from all bots)
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
        "আপনার মোট ব্যাংক সম্পত্তির মূল্য কত?"
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
        "ଆପଣଙ୍କୁ କେତେ ରିଣ ରକମ ଦରକାର?",
        "ଆପଣ କେଉଁ ପ୍ରକାରର ଋଣ ଦେଖୁଛନ୍ତି?",
        "ଆପଣଙ୍କ ବିଲାସୀ ସମ୍ପତ୍ତିର ମୂଲ୍ୟ କେତେ?",
        "ଆପଣଙ୍କ ମୋଟ ବ୍ୟାଙ୍କ ସମ୍ପତ୍ତିର ମୂଲ୍ୟ କେତେ?"
    ],
    "pa-IN": [
        "ਤੁਹਾਡੇ ਉੱਤੇ ਕਿੰਨੇ ਨਿਰਭਰ ਕਰਦੇ ਹਨ?",
        "ਤੁਸੀਂ ਕਿੰਨੇ ਮਹੀਨਿਆਂ ਲਈ ਕਰਜ਼ਾ ਚਾਹੁੰਦੇ ਹੋ?",
        "ਕੀ ਤੁਸੀਂ ਗ੍ਰੈਜੁਏਟ ਹੋ ਜਾਂ ਨਾ-ਗ੍ਰੈਜੁਏਟ?",
        "ਤੁਹਾਡੀ ਸਾਲਾਨਾ ਆਮਦਨ ਕਿੰਨੀ ਹੈ?",
        "ਤੁਹਾਡੀ ਰਿਹਾਇਸ਼ੀ ਸੰਪਤੀ ਦੀ ਕੀਮਤ ਕਿੰਨੀ ਹੈ?",
        "ਤੁਹਾਡੀ ਵਪਾਰਕ ਸੰਪਤੀ ਦੀ ਕੀਮਤ ਕਿੰਨੀ ਹੈ?",
        "ਕੀ ਤੁਸੀਂ ਸਵੈ-ਰੋਜ਼ਗਾਰ ਹੋ?",
        "ਤੁਹਾਨੂੰ ਕਿੰਨੀ ਕਰਜ਼ਾ ਰਕਮ ਦੀ ਲੋੜ ਹੈ?",
        "ਤੁਸੀਂ ਕਿਸ ਤਰ੍ਹਾਂ ਦਾ ਕਰਜ਼ਾ ਲੈਣਾ ਚਾਹੁੰਦੇ ਹੋ?",
        "ਤੁਹਾਡੀ ਵਿਲਾਸੀ ਸੰਪਤੀ ਦੀ ਕੀਮਤ ਕਿੰਨੀ ਹੈ?",
        "ਤੁਹਾਡੀ ਕੁੱਲ ਬੈਂਕ ਸੰਪਤੀ ਦੀ ਕੀਮਤ ਕਿੰਨੀ ਹੈ?"
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
conversation_sessions = {}
loan_eligibility_data = {}

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
    """Convert text to speech using Sarvam AI TTS API with enhanced speaker mapping."""
    url = "https://api.sarvam.ai/text-to-speech"
    
    config = LANGUAGE_CONFIG.get(target_language, LANGUAGE_CONFIG['en-IN'])
    chosen_speaker = speaker or config["speaker"]
    model = config["model"]
    text = text[:config["chunk_size"]]  # Use language-specific chunk size
    
    payload = {
        "inputs": [text],
        "target_language_code": target_language,
        "speaker": chosen_speaker,
        "pitch": 0,
        "pace": 1.0,
        "loudness": 1.0,
        "speech_sample_rate": 22050,
        "enable_preprocessing": True,
        "model": model
    }
    
    if target_language == "en-IN":
        payload["eng_interpolation_wt"] = 123
    
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

def perform_ocr(file_bytes, file_type):
    """Perform OCR using Tesseract, handling PDF to image conversion."""
    raw_text = ""
    
    if 'pdf' in file_type.lower():
        try:
            # For PDF files, convert to images first
            images = convert_from_bytes(file_bytes)
            
            for image in images:
                raw_text += pytesseract.image_to_string(image, lang='eng', config='--psm 3') + "\n\n"
        
        except Exception as e:
            raise Exception(f"PDF processing error: {e}")

    else:  # Process as standard image (PNG, JPEG, JPG, etc.)
        try:
            image = Image.open(BytesIO(file_bytes))
            raw_text = pytesseract.image_to_string(image, lang='eng', config='--psm 6')
        
        except Exception as e:
            raise Exception(f"Image processing error: {e}")

    if not raw_text.strip():
        raise Exception("OCR failed to extract any text from the document.")
        
    return raw_text

def calculate_loan_eligibility(applicant_data):
    """Calculate loan eligibility based on applicant data with detailed analysis."""
    try:
        name = applicant_data['name']
        age = applicant_data['age']
        credit_score = applicant_data['creditScore']
        income = applicant_data['income']
        employment_status = applicant_data['employmentStatus']
        loan_amount = applicant_data['loanAmount']
        loan_tenure = applicant_data['loanTenure']
        
        # Store data for AI reference
        user_key = f"{name}_{age}_{credit_score}"
        loan_eligibility_data[user_key] = {
            'name': name,
            'age': age,
            'credit_score': credit_score,
            'income': income,
            'employment_status': employment_status,
            'loan_amount': loan_amount,
            'loan_tenure': loan_tenure,
            'timestamp': str(uuid.uuid4())
        }
        
        suggestions = []
        eligible = True
        reason = ""
        recommended_emi = 0
        max_loan_amount = 0
        interest_rate = 12.0  # Default rate
        
        # Age criteria
        if age < 21 or age > 65:
            eligible = False
            reason = "Age must be between 21 and 65 years"
            suggestions.append("Wait until you are 21 or apply before turning 65")
        
        # Credit score criteria
        elif credit_score < 650:
            eligible = False
            reason = "Credit score is below minimum requirement (650)"
            suggestions.extend([
                "Improve your credit score by paying bills on time",
                "Reduce credit card utilization",
                "Check for errors in credit report"
            ])
        
        # Income criteria (minimum 3 lakhs annually)
        elif income < 300000:
            eligible = False
            reason = "Annual income is below minimum requirement (₹3,00,000)"
            suggestions.extend([
                "Consider applying after salary increase",
                "Look for lower loan amounts",
                "Consider a co-applicant with higher income"
            ])
        
        # Employment status criteria
        elif employment_status == "unemployed":
            eligible = False
            reason = "Unemployed applicants are not eligible for loans"
            suggestions.extend([
                "Secure employment before applying",
                "Consider business loans if self-employed",
                "Provide proof of alternative income sources"
            ])
        
        else:
            # Calculate eligibility for employed/self-employed
            # Debt-to-income ratio calculation (assuming 40% max)
            max_monthly_income = income / 12
            max_emi = max_monthly_income * 0.4
            
            # Calculate EMI using standard formula
            monthly_rate = (interest_rate / 100) / 12
            emi_multiplier = (monthly_rate * (1 + monthly_rate) ** loan_tenure) / ((1 + monthly_rate) ** loan_tenure - 1)
            calculated_emi = loan_amount * emi_multiplier
            
            if calculated_emi > max_emi:
                eligible = False
                reason = f"Requested EMI (₹{calculated_emi:.0f}) exceeds 40% of monthly income (₹{max_emi:.0f})"
                # Calculate maximum affordable loan
                max_loan_amount = max_emi / emi_multiplier
                suggestions.extend([
                    f"Consider reducing loan amount to ₹{max_loan_amount:.0f}",
                    f"Extend loan tenure to reduce EMI",
                    "Increase income or add a co-applicant"
                ])
            else:
                eligible = True
                recommended_emi = calculated_emi
                max_loan_amount = loan_amount
                
                # Adjust interest rate based on credit score
                if credit_score >= 750:
                    interest_rate = 10.5
                    reason = "Excellent credit score - eligible for premium rates"
                elif credit_score >= 700:
                    interest_rate = 11.5
                    reason = "Good credit score - eligible for competitive rates"
                else:
                    interest_rate = 12.5
                    reason = "Fair credit score - standard rates applicable"
                
                suggestions.extend([
                    "Maintain good credit score for better rates",
                    "Consider automatic EMI payments for discounts",
                    "Compare rates from multiple lenders"
                ])
        
        return {
            'eligible': eligible,
            'reason': reason,
            'recommendedEMI': int(recommended_emi) if recommended_emi > 0 else None,
            'suggestions': suggestions,
            'maxLoanAmount': int(max_loan_amount) if max_loan_amount > 0 else None,
            'interestRate': interest_rate
        }
        
    except Exception as e:
        logger.error(f"Error calculating loan eligibility: {e}")
        return {
            'eligible': False,
            'reason': f"Error in calculation: {str(e)}",
            'suggestions': ["Please check your input data and try again"],
            'recommendedEMI': None,
            'maxLoanAmount': None,
            'interestRate': None
        }

def calculate_loan_eligibility_deepseek(applicant_data):
    """Calculate loan eligibility using DeepSeek API (matches Node.js implementation)."""
    try:
        # Prepare the prompt exactly like the Node.js version
        prompt = f"""
        Analyze the following applicant details and determine if they are eligible for a loan:
        - Name: {applicant_data['name']}
        - Age: {applicant_data['age']}
        - Credit Score: {applicant_data['creditScore']}
        - Annual Income: {applicant_data['income']}
        - Employment Status: {applicant_data['employmentStatus']}

        Eligibility Criteria:
        - Age must be between 21 and 65.
        - Credit Score must be 650 or higher.
        - Annual Income must be at least $25,000.
        - Employment Status must be "employed" or "self-employed".

        Provide a response in the following JSON format:
        {{
            "eligible": true/false,
            "reason": "Brief explanation of the decision"
        }}
        """

        # Call the OpenRouter API (same as Node.js)
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
        )

        if response.status_code == 200:
            data = response.json()
            ai_response = data['choices'][0]['message']['content']
            
            # Parse the JSON response
            import json
            try:
                eligibility_result = json.loads(ai_response)
                # Ensure we have the required fields
                if 'eligible' in eligibility_result and 'reason' in eligibility_result:
                    return {
                        'eligible': eligibility_result['eligible'],
                        'reason': eligibility_result['reason'],
                        'suggestions': [],
                        'recommendedEMI': None,
                        'maxLoanAmount': None,
                        'interestRate': None
                    }
            except json.JSONDecodeError:
                logger.error(f"Failed to parse DeepSeek response: {ai_response}")
        
        # Fallback if API call fails
        return calculate_loan_eligibility(applicant_data)
        
    except Exception as e:
        logger.error(f"DeepSeek API error: {e}")
        # Fallback to local calculation
        return calculate_loan_eligibility(applicant_data)

@app.route('/')
def home():
    """ API Status endpoint """
    return jsonify({
        "status": "CrediBot API Running",
        "version": "1.0",
        "endpoints": [
            "/chat",
            "/translate",
            "/text-to-speech",
            "/speech-to-text",
            "/read-document",
            "/set-language",
            "/get-languages"
        ],
        "languages_supported": len(LANGUAGES),
        "features": ["AI Chat", "TTS", "STT", "Translation", "OCR"]
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "groq_available": groq_client is not None,
        "sarvam_available": bool(SARVAM_API_KEY),
        "deepseek_available": deepseek_available
    })


@app.route('/get-languages', methods=['GET'])
def get_languages():
    """Get all supported languages."""
    return jsonify({
        "languages": LANGUAGES,
        "default": "en-IN"
    })


@app.route('/speech-to-text', methods=['POST'])
def speech_to_text_endpoint():
    """Convert speech to text using Sarvam AI STT API."""
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files['audio']
        language_code = request.form.get('language_code', 'en-IN')

        if audio_file.filename == '':
            return jsonify({"error": "No audio file selected"}), 400

        # Read audio file
        audio_data = audio_file.read()

        # Convert speech to text
        transcript = speech_to_text(audio_data, language_code)

        if transcript:
            return jsonify({
                "success": True,
                "transcript": transcript,
                "language": language_code
            })
        else:
            return jsonify({"error": "Failed to transcribe audio"}), 500

    except Exception as e:
        logger.error(f"STT endpoint error: {e}")
        return jsonify({"error": str(e)}), 500


def speech_to_text(audio_data, source_language='en-IN'):
    """Convert speech to text using Sarvam AI STT API."""
    url = "https://api.sarvam.ai/speech-to-text"

    try:
        # Prepare the audio file for upload
        files = {
            'file': ('audio.wav', audio_data, 'audio/wav')
        }

        data = {
            'language_code': source_language,
            'with_timestamps': 'false',
            'enable_preprocessing': 'true'
        }

        headers = {
            'api-subscription-key': SARVAM_API_KEY
        }

        response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
        response.raise_for_status()
        response_data = response.json()

        if 'transcript' in response_data:
            return response_data['transcript']
        return None

    except Exception as e:
        logger.error(f"STT error: {e}")
        return None


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
    """Convert text to speech and return actual audio file."""
    try:
        data = request.get_json()
        inputs = data.get('inputs', [])
        target_language_code = data.get('target_language_code', 'en-IN')
        speaker = data.get('speaker')
        
        if not inputs:
            return jsonify({"error": "No input text provided"}), 400
            
        text = inputs[0]

        # Get audio data from Sarvam API
        config = LANGUAGE_CONFIG.get(target_language_code, LANGUAGE_CONFIG['en-IN'])
        model = config["model"]
        chunk_size = config["chunk_size"]
        silence_bytes = config["silence_bytes"]
        chosen_speaker = speaker or config["speaker"]

        # Process text in chunks for better quality
        audio_data_combined = BytesIO()
        silence_chunk = b"\x00" * silence_bytes
        text_chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

        for chunk in text_chunks:
            if not chunk.strip():
                continue

            request_body = {
                "inputs": [chunk],
                "target_language_code": target_language_code,
                "speaker": chosen_speaker,
                "pitch": 0,
                "pace": 1.0,
                "loudness": 1.0,
                "speech_sample_rate": 22050,
                "enable_preprocessing": True,
                "model": model
            }
            
            if target_language_code == "en-IN":
                request_body["eng_interpolation_wt"] = 123

            headers = {
                "api-subscription-key": SARVAM_API_KEY,
                "Content-Type": "application/json"
            }

            response = requests.post("https://api.sarvam.ai/text-to-speech", headers=headers, json=request_body)
            if response.status_code != 200:
                logger.error(f"TTS API error for chunk: {response.text}")
                continue

            result = response.json()
            if "audios" in result and result["audios"]:
                audio_data_combined.write(base64.b64decode(result["audios"][0]))
                audio_data_combined.write(silence_chunk)

        if audio_data_combined.getbuffer().nbytes <= silence_bytes:
            return jsonify({"error": "Failed to generate audio"}), 500

        # Save audio to file and return file path
        audio_filename = f"tts_{uuid.uuid4().hex[:8]}.wav"
        audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)

        with open(audio_path, 'wb') as f:
            audio_data_combined.seek(0)
            f.write(audio_data_combined.read())

        # Return the audio file
        return send_file(audio_path, mimetype="audio/wav", as_attachment=False)
            
    except Exception as e:
        logger.error(f"TTS endpoint error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle general chat messages with Groq support."""
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
        
        # Choose AI model based on request
        if groq_client:
            # Initialize Groq conversation session
            if session_id not in conversation_sessions:
                conversation_sessions[session_id] = {
                    "messages": [],
                    "question_count": 0,
                    "prompt_added": False
                }
            
            session = conversation_sessions[session_id]
            
            # Add system prompt only once
            if not session["prompt_added"]:
                system_prompt = '''You are a friendly, professional, and highly knowledgeable loan assistant. Your goal is to help users understand their loan eligibility in an interactive and engaging manner. Start by warmly greeting the user and asking for basic details step by step. Ask brief, clear questions to avoid overwhelming the user. Don't use any special characters or formatting in your responses.'''
                session["messages"].append({"role": "system", "content": system_prompt})
                session["prompt_added"] = True
            
            session["messages"].append({"role": "user", "content": message})
            session["question_count"] += 1
            
            try:
                chat_completion = groq_client.chat.completions.create(
                    messages=session["messages"],
                    model="llama-3.3-70b-versatile"
                )
                bot_response = chat_completion.choices[0].message.content
                session["messages"].append({"role": "assistant", "content": bot_response})
            except Exception as e:
                logger.error(f"Groq API error: {e}")
                bot_response = "I apologize, but I'm having trouble processing your request right now. Please try again later."
        
        if not bot_response:
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
        
        # Generate eligibility assessment
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
        
        eligibility_result = ""

        if groq_client:
            try:
                chat_completion = groq_client.chat.completions.create(
                    messages=[{"role": "system", "content": prompt}],
                    model="llama-3.3-70b-versatile"
                )
                eligibility_result = chat_completion.choices[0].message.content
            except Exception as e:
                logger.error(f"Groq API error in eligibility check: {e}")
        
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
        logger.error(f"Check eligibility error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/read-document', methods=['POST'])
def read_document():
    """Process uploaded document with OCR and provide vernacular explanation - supports both PDF and images."""
    try:
        if 'document' not in request.files:
            return jsonify({"error": "No document uploaded"}), 400
        
        file = request.files['document']
        language_code = request.form.get('language_code', 'en-IN')
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Check file type - support both PDF and images
        allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        file_ext = os.path.splitext(file.filename.lower())[1]

        if file_ext not in allowed_extensions:
            return jsonify({
                               "error": f"Unsupported file type. Supported: {', '.join(allowed_extensions)}"}), 400

        # Read file content
        file_bytes = file.read()
        
        try:
            # 1. Perform OCR to extract text
            raw_text = perform_ocr(file_bytes, file.content_type)
            
            if not raw_text.strip():
                return jsonify({"error": "Could not extract text from the document"}), 400

            # 2. Use AI to simplify and explain (prefer Groq for document analysis)
            system_prompt = f"""You are an expert financial explainer for first-time loan applicants. Your task is to analyze the following loan document text.
            
            ## Summary of Key Loan Terms
            1. Summarize the Key Terms (Interest Rate, Tenure, EMI, Prepayment Penalty) in a bulleted list.
            
            ## Risks and Commitments Explained
            2. Provide a simple explanation of the main risks and commitments in the document.
            
            3. Convert all financial jargon into plain language with relatable examples.
            
            4. The response must be in English for translation.
            
            Document Text:
            ---
            {raw_text[:4000]}
            ---
            """

            english_explanation = ""
            
            if groq_client:
                try:
                    chat_completion = groq_client.chat.completions.create(
                        messages=[{"role": "system", "content": system_prompt}],
                        model="llama-3.3-70b-versatile"
                    )
                    english_explanation = chat_completion.choices[0].message.content
                except Exception as e:
                    logger.error(f"Groq error in document processing: {e}")
            
            elif gemini_model:
                try:
                    response = gemini_model.generate_content(system_prompt)
                    english_explanation = response.text
                except Exception as e:
                    logger.error(f"Gemini error in document processing: {e}")
            else:
                english_explanation = """
                This appears to be a loan agreement document. Based on the content, here are the key points:
                
                1. Loan Amount: As specified in the document
                2. Interest Rate: Please verify the annual percentage rate
                3. Repayment Terms: Check the monthly installment amount and tenure
                4. Important Clauses: Review all terms and conditions carefully
                5. Required Actions: Ensure all signatures and documentation are complete
                
                Please review all terms carefully before signing.
                """

            # 3. Translate to requested language
            vernacular_explanation = english_explanation
            if language_code != "en-IN":
                vernacular_explanation = translate_text(
                    english_explanation,
                    "en-IN",
                    language_code
                )
            
            return jsonify({
                "success": True,
                "raw_text": raw_text,
                "english_explanation": english_explanation,
                "vernacular_explanation": vernacular_explanation,
                "language": language_code,
                "file_type": file_ext
            })

        except Exception as e:
            logger.error(f"Document processing error: {e}")
            return jsonify({"error": f"Failed to process document: {str(e)}"}), 500
        
    except Exception as e:
        logger.error(f"Document processing error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/check-eligibility', methods=['POST'])
def check_loan_eligibility_form():
    """Check loan eligibility based on form data (matches HTML form functionality)."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'age', 'creditScore', 'income', 'employmentStatus', 'loanAmount', 'loanTenure']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Try DeepSeek API first (matches Node.js implementation)
        if DEEPSEEK_API_KEY:
            result = calculate_loan_eligibility_deepseek(data)
        else:
            # Fallback to local calculation
            result = calculate_loan_eligibility(data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Loan eligibility check error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('audio', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    logger.info("Starting CrediBot Complete Flask API Server...")
    logger.info(f"Groq API Status: {'Available' if groq_client else 'Not Available'}")
    logger.info(f"Sarvam API Status: {'Available' if SARVAM_API_KEY else 'Not Available'}")
    logger.info(f"DeepSeek API Status: {'Available' if deepseek_available else 'Not Available'}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
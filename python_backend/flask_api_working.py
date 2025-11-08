import os
import random
import uuid
import base64
import requests
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import tempfile
import logging
from groq import Groq

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# API Keys
SARVAM_API_KEY = "sk_uttanwco_NUp2bWPxXWW3xhZiV0YXp6nE"
GROQ_API_KEY = "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"

# Initialize Groq client
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
    logger.info("Groq API initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    groq_client = None

# Global session storage
user_sessions = {}
conversation_sessions = {}


@app.route('/')
def home():
    """API Status endpoint"""
    return jsonify({
        "status": "CrediBot API Running",
        "version": "1.0",
        "endpoints": ["/chat", "/translate", "/text-to-speech", "/speech-to-text", "/set-language"],
        "languages_supported": 11,
        "features": ["AI Chat", "TTS", "STT", "Translation"]
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "groq_available": groq_client is not None,
        "sarvam_available": bool(SARVAM_API_KEY)
    })


@app.route('/set-language', methods=['POST'])
def set_language():
    """Set user's preferred language"""
    try:
        data = request.get_json()
        language_code = data.get('language_code', 'en-IN')

        return jsonify({
            "success": True,
            "language_code": language_code,
            "message": f"Language set to {language_code}"
        })
    except Exception as e:
        logger.error(f"Set language error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages using Groq"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        language_code = data.get('languageCode', 'en-IN')
        user_id = data.get('userId', str(uuid.uuid4()))
        is_greeting = data.get('isGreeting', False)

        # Initialize conversation session
        if user_id not in conversation_sessions:
            conversation_sessions[user_id] = {
                "messages": [],
                "question_count": 0,
                "prompt_added": False
            }

        session = conversation_sessions[user_id]

        # Add system prompt only once
        if not session["prompt_added"]:
            system_prompt = '''You are CrediBot, a friendly, professional, and highly knowledgeable loan assistant for Indian banking. Your goal is to help users understand their loan eligibility in an interactive and engaging manner. Start by warmly greeting the user and asking for basic details like name and age, then ask required details step by step (e.g., type of loan, loan amount, tenure, age, income, credit score, etc.) instead of requesting everything at once. Ask brief, clear questions to avoid overwhelming the user. Always respond in plain text without special characters or formatting.'''
            session["messages"].append({"role": "system", "content": system_prompt})
            session["prompt_added"] = True

        # Handle initial greeting
        if is_greeting or message == "initial_greeting":
            user_message_to_llm = "Start the conversation with a warm greeting and ask the first step question."
        else:
            user_message_to_llm = message
            session["messages"].append({"role": "user", "content": message})
            session["question_count"] += 1

        # Get AI response using Groq
        if groq_client:
            try:
                chat_completion = groq_client.chat.completions.create(
                    messages=session["messages"],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                    max_tokens=512
                )
                bot_response = chat_completion.choices[0].message.content
                session["messages"].append({"role": "assistant", "content": bot_response})

            except Exception as e:
                logger.error(f"Groq API error: {e}")
                bot_response = "I apologize, but I'm having trouble processing your request right now. Please try again later."
        else:
            bot_response = "I'm here to help with your loan and banking questions. Please ask me anything about loan eligibility, documentation, or financial advice."

        return jsonify({
            "response": bot_response,
            "questions_asked": session["question_count"],
            "session_id": user_id
        })

    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/translate', methods=['POST'])
def translate():
    """Translate text using Sarvam API"""
    try:
        data = request.get_json()
        input_text = data.get('input', '')
        source_language_code = data.get('source_language_code', 'en-IN')
        target_language_code = data.get('target_language_code', 'en-IN')

        if not input_text:
            return jsonify({"error": "No input text provided"}), 400

        if source_language_code == target_language_code:
            return jsonify({"translated_text": input_text})

        url = "https://api.sarvam.ai/translate"
        payload = {
            "input": input_text[:1000],  # Limit text length
            "source_language_code": source_language_code,
            "target_language_code": target_language_code,
            "speaker_gender": "Female",
            "mode": "formal",
            "model": "mayura:v1",
            "enable_preprocessing": False
        }

        headers = {
            "Content-Type": "application/json",
            "api-subscription-key": SARVAM_API_KEY
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            response_data = response.json()
            if "translated_text" in response_data:
                return jsonify({"translated_text": response_data["translated_text"]})

        return jsonify({"translated_text": input_text})  # Fallback to original text

    except Exception as e:
        logger.error(f"Translation error: {e}")
        return jsonify({"translated_text": input_text}), 200  # Graceful fallback


@app.route('/text-to-speech', methods=['POST'])
def text_to_speech_endpoint():
    """Convert text to speech using Sarvam API"""
    try:
        data = request.get_json()
        inputs = data.get('inputs', [])
        target_language_code = data.get('targetLanguageCode', 'en-IN')

        if not inputs:
            return jsonify({"error": "No input text provided"}), 400

        text = inputs[0][:500]  # Limit text length

        # Speaker mapping
        speakers = {
            "hi-IN": "meera", "bn-IN": "tavithra", "gu-IN": "maitreyi",
            "kn-IN": "arvind", "ml-IN": "amol", "mr-IN": "amartya",
            "od-IN": "diya", "pa-IN": "neel", "ta-IN": "misha",
            "te-IN": "vian", "en-IN": "arjun"
        }

        speaker = speakers.get(target_language_code, "meera")

        url = "https://api.sarvam.ai/text-to-speech"
        payload = {
            "inputs": [text],
            "target_language_code": target_language_code,
            "speaker": speaker,
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

        response = requests.post(url, json=payload, headers=headers, timeout=15)

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("audios"):
                audio_base64 = response_data["audios"][0]
                audio_bytes = base64.b64decode(audio_base64)

                # Create temporary file and return audio
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                temp_file.write(audio_bytes)
                temp_file.close()

                return send_file(temp_file.name, mimetype='audio/wav', as_attachment=False)

        return jsonify({"error": "Failed to generate audio"}), 500

    except Exception as e:
        logger.error(f"TTS error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    """Convert speech to text - placeholder"""
    try:
        return jsonify({
            "response": "Speech recognition is being processed. Please type your message for now."
        })
    except Exception as e:
        logger.error(f"STT error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    logger.info("Starting CrediBot Working Flask API Server...")
    logger.info(f"Groq API Status: {'Available' if groq_client else 'Not Available'}")
    logger.info(f"Sarvam API Status: {'Available' if SARVAM_API_KEY else 'Not Available'}")

    app.run(host='0.0.0.0', port=5000, debug=True)

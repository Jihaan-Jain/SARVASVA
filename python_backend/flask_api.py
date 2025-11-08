import os
import random
import uuid
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

# Loan questions in different languages (from your bot.py)
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
    # Add other languages as needed...
}

# Store user session data
user_sessions = {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "gemini_api": "available" if model else "unavailable"
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
            """
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            bot_response = response.text
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
    """Translation endpoint"""
    try:
        data = request.json
        input_text = data.get('input', '')
        source_lang = data.get('source_language_code', 'en-IN')
        target_lang = data.get('target_language_code', 'en-IN')
        
        if source_lang == target_lang:
            return jsonify({
                "translated_text": input_text,
                "success": True
            })
        
        if model:
            source_name = LANGUAGES.get(source_lang, 'English')
            target_name = LANGUAGES.get(target_lang, 'English')
            
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
            
            translated_text = response.text.strip()
        else:
            translated_text = input_text  # Fallback
        
        return jsonify({
            "translated_text": translated_text,
            "success": True
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
        # In production, you would integrate with a TTS service
        return jsonify({
            "success": True,
            "message": "TTS not implemented yet"
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
        # In production, you would integrate with STT service
        return jsonify({
            "transcription": "This is a mock transcription",
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
            a clear explanation in {language_name} about:
            1. What type of document this is
            2. Key information contained in the document
            3. How this document relates to loan applications
            4. Any important details the user should understand
            
            Document content: {document_text}
            
            Provide a helpful, easy-to-understand explanation.
            """
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            explanation = response.text
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

# Loan-specific endpoints
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
    """Check loan eligibility based on answers"""
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
            # Create detailed prompt for loan eligibility
            answers_text = "\n".join([f"- {q}: {a}" for q, a in answers.items()])
            
            prompt = f"""
            Act as a professional Indian bank loan advisor. Analyze the following financial details 
            and provide a comprehensive loan eligibility assessment:

            Financial Profile:
            {answers_text}

            Provide your response in {language_name} with the following structure:
            1. ELIGIBILITY STATUS: Clearly state if the loan is APPROVED or REJECTED
            2. DETAILED ANALYSIS: Explain the reasoning behind your decision
            3. RECOMMENDATIONS: Provide 3-5 specific actionable recommendations
            4. REQUIRED DOCUMENTS: List all necessary documents for loan application
            5. NEXT STEPS: Clear guidance on what to do next

            Make your response professional, empathetic, and specific to Indian banking context.
            """
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            eligibility_result = response.text
            
            # Determine eligibility from response (simple keyword check)
            is_eligible = "approved" in eligibility_result.lower() or "eligible" in eligibility_result.lower()
            
            # Extract recommendations and documents (simplified)
            recommendations = [
                "Maintain a good credit score",
                "Ensure all documents are up to date",
                "Consider a co-applicant if needed",
                "Compare interest rates from different banks"
            ]
            
            required_documents = [
                "Identity Proof (Aadhar Card/PAN Card)",
                "Address Proof (Utility Bills/Rent Agreement)",
                "Income Proof (Salary Slips/ITR)",
                "Bank Statements (6 months)",
                "Employment Certificate"
            ]
            
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
            "success": True
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
    print("🚀 Starting CrediBot Flask API Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("🔧 Make sure to update your Android app's BASE_URL accordingly")
    app.run(host='0.0.0.0', port=8000, debug=True)
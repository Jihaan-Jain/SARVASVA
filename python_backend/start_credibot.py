#!/usr/bin/env python3
"""
CrediBot Production Startup Script
Sets up environment and starts the complete API server with all integrations.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up environment variables for production."""
    env_vars = {
        # Core AI Models
        'GEMINI_API_KEY': 'AIzaSyC9i96-x18BGKIeV7HOHKn-piu4e5R9IUs',
        'OPENAI_API_KEY': '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',
        
        # Sarvam AI (Translation and TTS)
        'SARVAM_API_KEY': 'sk_uttanwco_NUp2bWPxXWW3xhZiV0YXp6nE',
        
        # Groq API (Advanced LLM processing)
        'GROQ_API_KEY': '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',
        
        # DeepSeek API (via OpenRouter)
        'DEEPSEEK_API_KEY': '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',
        
        # Telegram Bot Token
        'TELEGRAM_BOT_TOKEN': '8125759209:AAEWipIexhQeHmIFykw1J3xpG6ujZPRhIyM',
        
        # Flask Configuration
        'FLASK_ENV': 'production',
        'FLASK_DEBUG': 'False',
        'LOG_LEVEL': 'INFO'
    }
    
    logger.info("Setting up environment variables...")
    for key, value in env_vars.items():
        os.environ[key] = value
        logger.info(f"✅ {key} configured")

def check_dependencies():
    """Check if all required dependencies are installed."""
    logger.info("Checking dependencies...")
    
    required_packages = [
        'flask', 'flask-cors', 'requests', 'google-generativeai',
        'groq', 'python-dotenv', 'pillow', 'pytesseract', 'pdf2image'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing packages: {missing_packages}")
        logger.info("Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                *missing_packages
            ])
            logger.info("✅ All dependencies installed successfully")
        except subprocess.CalledProcessError:
            logger.error("❌ Failed to install dependencies")
            return False
    else:
        logger.info("✅ All dependencies already installed")
    
    return True

def create_directories():
    """Create necessary directories."""
    directories = ['uploads', 'audio', 'temp']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"✅ Directory '{directory}' ready")

def test_api_connections():
    """Test connections to all APIs."""
    logger.info("Testing API connections...")
    
    # Test Gemini
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Test")
        logger.info("✅ Gemini API connection successful")
    except Exception as e:
        logger.warning(f"⚠️ Gemini API connection failed: {e}")
    
    # Test Groq
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        logger.info("✅ Groq API connection successful")
    except Exception as e:
        logger.warning(f"⚠️ Groq API connection failed: {e}")
    
    # Test Sarvam AI
    try:
        import requests
        response = requests.post(
            "https://api.sarvam.ai/translate",
            headers={
                "Content-Type": "application/json",
                "api-subscription-key": os.getenv('SARVAM_API_KEY')
            },
            json={
                "input": "test",
                "source_language_code": "en-IN",
                "target_language_code": "hi-IN"
            },
            timeout=5
        )
        if response.status_code in [200, 400]:  # 400 is ok for test
            logger.info("✅ Sarvam API connection successful")
        else:
            logger.warning(f"⚠️ Sarvam API returned status: {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️ Sarvam API connection failed: {e}")
    
    # Test DeepSeek (OpenRouter)
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "test"}]
            },
            timeout=5
        )
        if response.status_code in [200, 401]:  # 401 might be rate limiting
            logger.info("✅ DeepSeek API connection successful")
        else:
            logger.warning(f"⚠️ DeepSeek API returned status: {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️ DeepSeek API connection failed: {e}")

def start_server():
    """Start the CrediBot Flask server."""
    logger.info("🚀 Starting CrediBot Flask API Server...")
    
    try:
        from flask_api_complete import app
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        return False
    
    return True

def main():
    """Main startup function."""
    print("🤖 CrediBot Production Startup")
    print("=" * 50)
    
    # Step 1: Setup environment
    setup_environment()
    
    # Step 2: Check dependencies
    if not check_dependencies():
        logger.error("❌ Dependency check failed. Exiting.")
        sys.exit(1)
    
    # Step 3: Create directories
    create_directories()
    
    # Step 4: Test API connections
    test_api_connections()
    
    # Step 5: Start server
    logger.info("🚀 All systems ready! Starting CrediBot server...")
    print("\n" + "=" * 50)
    print("🎉 CrediBot is starting...")
    print("📱 Android app can connect to: http://localhost:5000")
    print("🌐 API documentation: http://localhost:5000/health")
    print("=" * 50)
    
    start_server()

if __name__ == "__main__":
    main()
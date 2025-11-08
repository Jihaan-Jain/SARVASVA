#!/usr/bin/env python3
"""
CrediBot Production Startup Script
Automatically sets up environment and starts the complete multilingual banking assistant
"""
import os
import sys
import subprocess
import platform

def set_environment_variables():
    """Set all required API keys in the environment"""
    print("🔧 Setting up environment variables...")
    
    # API Keys from user
    api_keys = {
        'SARVAM_API_KEY': 'sk_uttanwco_NUp2bWPxXWW3xhZiV0YXp6nE',
        'OPENAI_API_KEY': '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',
        'GROQ_API_KEY': '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',
        'DEEPSEEK_API_KEY': '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',
        'GEMINI_API_KEY': 'default_key'  # Optional fallback
    }
    
    for key, value in api_keys.items():
        os.environ[key] = value
        print(f"✅ {key} set")
    
    print("🎉 All API keys configured!")

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'flask', 'flask-cors', 'requests', 'python-dotenv',
        'groq', 'google-generativeai', 'pdf2image', 'pytesseract', 
        'pillow', 'werkzeug'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MISSING")
    
    if missing_packages:
        print(f"\n🔧 Installing missing packages: {', '.join(missing_packages)}")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
        print("✅ All dependencies installed!")
    else:
        print("🎉 All dependencies are ready!")

def setup_ocr_dependencies():
    """Setup OCR dependencies (Tesseract and Poppler)"""
    print("🔍 Setting up OCR dependencies...")
    
    system = platform.system().lower()
    
    if system == 'windows':
        print("📝 Windows detected - Please ensure:")
        print("   1. Tesseract is installed and added to PATH")
        print("   2. Poppler is installed (download from: https://github.com/oschwartz10612/poppler-windows/releases/)")
        print("   3. Update the paths in the Flask API if needed")
        
        # Default Windows paths
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        poppler_path = r'C:\Users\jainj\Downloads\Release-25.07.0-0\poppler-25.07.0\Library\bin'
        
        print(f"   Default Tesseract path: {tesseract_path}")
        print(f"   Default Poppler path: {poppler_path}")
        print("   ✅ If paths are correct, OCR will work!")
        
    elif system == 'linux':
        print("🐧 Linux detected - Installing OCR dependencies...")
        try:
            subprocess.check_call(['sudo', 'apt-get', 'update'])
            subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'tesseract-ocr', 'poppler-utils'])
            print("✅ OCR dependencies installed!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install OCR dependencies. Please install manually:")
            print("   sudo apt-get install tesseract-ocr poppler-utils")
    
    elif system == 'darwin':
        print("🍎 macOS detected - Installing OCR dependencies...")
        try:
            subprocess.check_call(['brew', 'install', 'tesseract', 'poppler'])
            print("✅ OCR dependencies installed!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install OCR dependencies. Please install manually:")
            print("   brew install tesseract poppler")

def start_server():
    """Start the Flask server"""
    print("🚀 Starting CrediBot Production Server...")
    print("\n" + "="*60)
    print("🎉 CREDIBOT MULTILINGUAL BANKING ASSISTANT")
    print("="*60)
    print("📱 Features Available:")
    print("   ✅ 11 Indian Language Support")
    print("   ✅ Real AI Conversations (Gemini + Groq)")
    print("   ✅ Professional Translation (Sarvam AI)")
    print("   ✅ Native Voice Synthesis (TTS)")
    print("   ✅ Document OCR Processing")
    print("   ✅ Loan Eligibility Assessment")
    print("   ✅ Form-based + Chat Interface")
    print("="*60)
    print("🌐 Server will start on: http://localhost:5000")
    print("📱 Android app should connect to: http://10.0.2.2:5000")
    print("="*60)
    
    try:
        # Import and run the Flask app
        from flask_api_complete import app
        app.run(host='0.0.0.0', port=5000, debug=False)
    except ImportError:
        print("❌ Flask API not found. Starting alternative server...")
        # Try to run the file directly
        subprocess.run([sys.executable, 'flask_api_complete.py'])

def main():
    """Main startup function"""
    print("🎉 Starting CrediBot Production Setup...")
    print("=" * 50)
    
    # Setup environment
    set_environment_variables()
    print()
    
    # Check dependencies
    check_dependencies()
    print()
    
    # Setup OCR
    setup_ocr_dependencies()
    print()
    
    # Start server
    start_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 CrediBot server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting CrediBot: {e}")
        print("Please check the logs and try again.")
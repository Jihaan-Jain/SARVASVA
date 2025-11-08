#!/usr/bin/env python3
"""
CrediBot Backend Setup and Runner Script
This script handles the complete setup and running of the CrediBot Flask backend
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print the application banner"""
    print("=" * 60)
    print("🚀 CrediBot Backend Setup & Runner")
    print("=" * 60)
    print("📱 Multilingual Loan Assistant Backend")
    print("🤖 Powered by Google Gemini AI + Sarvam AI Translation")
    print("🌐 Flask REST API for Android App")
    print("=" * 60)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        print("   Please upgrade Python and try again")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True

def setup_virtual_environment():
    """Set up a virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✅ Virtual environment created successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to create virtual environment")
            return False
    else:
        print("✅ Virtual environment already exists")
    
    return True

def get_activation_command():
    """Get the command to activate virtual environment based on OS"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Determine the correct pip path
    if platform.system() == "Windows":
        pip_path = "venv\\Scripts\\pip"
    else:
        pip_path = "venv/bin/pip"
    
    try:
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("💡 Try running: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and guide user to create it"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("⚠️  Environment file (.env) not found")
        print("📝 Please create a .env file with your API keys:")
        print()
        print("   1. Copy .env.example to .env")
        print("   2. Fill in your actual API keys:")
        print("      - GEMINI_API_KEY (from Google AI Studio)")
        print("      - SARVAM_API_KEY (from Sarvam AI)")
        print()
        print("🔧 Example .env content:")
        print("   GEMINI_API_KEY=your_actual_gemini_api_key")
        print("   SARVAM_API_KEY=your_actual_sarvam_api_key")
        print()
        
        create_env = input("❓ Would you like to create .env file now? (y/n): ").lower()
        if create_env == 'y':
            gemini_key = input("🔑 Enter your Gemini API key: ").strip()
            sarvam_key = input("🔑 Enter your Sarvam API key (optional): ").strip()
            
            with open(".env", "w") as f:
                f.write(f"GEMINI_API_KEY={gemini_key}\n")
                if sarvam_key:
                    f.write(f"SARVAM_API_KEY={sarvam_key}\n")
                f.write("FLASK_PORT=8000\n")
                f.write("FLASK_HOST=0.0.0.0\n")
                f.write("FLASK_DEBUG=true\n")
            
            print("✅ .env file created successfully")
            return True
        else:
            print("⏭️  Continuing without .env file (API keys must be set manually)")
            return False
    else:
        print("✅ Environment file (.env) found")
        return True

def load_environment():
    """Load environment variables from .env file"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
        
        # Check critical API keys
        gemini_key = os.getenv('GEMINI_API_KEY')
        sarvam_key = os.getenv('SARVAM_API_KEY')
        
        print(f"🔑 Gemini API Key: {'✅ Set' if gemini_key else '❌ Missing'}")
        print(f"🔑 Sarvam API Key: {'✅ Set' if sarvam_key else '⚠️ Missing (will use Gemini fallback)'}")
        
        if not gemini_key:
            print("❌ Critical: Gemini API key is required for the bot to function")
            return False
            
        return True
        
    except ImportError:
        print("⚠️  python-dotenv not installed, skipping .env file loading")
        return True

def start_server():
    """Start the Flask server"""
    print()
    print("🚀 Starting CrediBot Flask API Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("🔧 For Android testing:")
    print("   📱 Emulator: Use http://10.0.2.2:8000 in your app")
    print("   📱 Real device: Use http://YOUR_COMPUTER_IP:8000 in your app")
    print()
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Import and run the Flask app
        from flask_api_enhanced import app
        app.run(host='0.0.0.0', port=8000, debug=True)
        
    except ImportError:
        print("❌ Could not import flask_api_enhanced.py")
        print("   Make sure flask_api_enhanced.py exists in this directory")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def main():
    """Main setup and run function"""
    print_banner()
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Set up virtual environment
    if not setup_virtual_environment():
        print("❌ Setup failed at virtual environment creation")
        sys.exit(1)
    
    # Step 3: Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        print("💡 You can try installing manually with:")
        print(f"   {get_activation_command()}")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Step 4: Check environment configuration
    env_ready = check_env_file()
    
    # Step 5: Load environment variables
    if not load_environment():
        print("❌ Critical environment variables missing")
        sys.exit(1)
    
    # Step 6: Start the server
    print("🎯 Setup completed successfully!")
    print()
    input("Press Enter to start the server...")
    
    if not start_server():
        sys.exit(1)

if __name__ == '__main__':
    main()
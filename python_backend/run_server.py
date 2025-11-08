#!/usr/bin/env python3
"""
CrediBot Flask API Server Runner
Run this script to start the backend server for the Android app
"""

import os
import sys
from flask_api import app

def main():
    print("🚀 Starting CrediBot Flask API Server...")
    print("=" * 50)
    print("📱 Android App Backend Server")
    print("🌐 Server URL: http://localhost:8000")
    print("🔧 Make sure your Android app points to this URL")
    print("💡 For real device testing, use your computer's IP address")
    print("=" * 50)
    
    try:
        # Check if required environment variables are set
        if not os.getenv('GEMINI_API_KEY'):
            print("⚠️  Warning: GEMINI_API_KEY not found in environment")
            print("   The server will run but AI responses may be limited")
        
        print("✅ Starting server on 0.0.0.0:8000...")
        app.run(
            host='0.0.0.0', 
            port=8000, 
            debug=True,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
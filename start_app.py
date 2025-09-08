#!/usr/bin/env python3
"""
Startup script for the NLP Travel Chatbot application.
This script helps users start the backend server easily.
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        'AMADEUS_API_KEY',
        'AMADEUS_API_SECRET', 
        'BOOKING_API_KEY',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file in the backend directory with your API keys.")
        print("You can use env_template.txt as a reference.")
        return False
    
    print("✅ All required environment variables found!")
    return True

def start_backend():
    """Start the FastAPI backend server"""
    backend_dir = Path(__file__).parent / "backend"
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    print("🚀 Starting backend server...")
    print("📍 Backend will be available at: http://localhost:8000")
    print("📖 API documentation at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Change to backend directory and start uvicorn
        os.chdir(backend_dir)
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

def open_frontend():
    """Open the frontend in the default browser"""
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    
    if frontend_path.exists():
        print(f"🌐 Opening frontend: {frontend_path}")
        webbrowser.open(f"file://{frontend_path.absolute()}")
    else:
        print("❌ Frontend file not found!")

def main():
    """Main function"""
    print("🛫 NLP Travel Chatbot - Startup Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("backend").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("\n💡 To set up your environment:")
        print("1. Copy backend/env_template.txt to backend/.env")
        print("2. Fill in your actual API keys")
        print("3. Run this script again")
        sys.exit(1)
    
    print("\n🎯 Starting application...")
    
    # Start backend
    start_backend()

if __name__ == "__main__":
    main()

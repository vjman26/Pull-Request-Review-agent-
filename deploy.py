#!/usr/bin/env python3
"""
Deployment script for PR Review Agent Web App
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_web.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = ['templates', 'static/css', 'static/js']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created {directory}/")

def run_app():
    """Run the Flask application"""
    print("🚀 Starting PR Review Agent Web App...")
    print("📍 Access the app at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    """Main deployment function"""
    print("🔍 PR Review Agent - Web Deployment")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ app.py not found. Please run this script from the project root directory.")
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Create directories
    create_directories()
    
    # Run the app
    run_app()

if __name__ == "__main__":
    main()

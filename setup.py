#!/usr/bin/env python3
"""
Setup script for AI Resume Summarizer & Career Navigator
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        sys.exit(1)

def setup_environment():
    """Setup environment file"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("📝 Creating .env file from template...")
            env_file.write_text(env_example.read_text())
            print("✅ .env file created")
            print("⚠️  Please edit .env file and add your API keys")
        else:
            print("❌ .env.example not found")
    else:
        print("✅ .env file already exists")

def check_data_file():
    """Check if jobs data file exists"""
    data_file = Path("data/jobs.csv")
    if data_file.exists():
        print(f"✅ Jobs dataset found: {len(open(data_file).readlines())} records")
    else:
        print("⚠️  Jobs dataset not found at data/jobs.csv")

def main():
    """Main setup function"""
    print("🚀 Setting up AI Resume Summarizer & Career Navigator")
    print("=" * 50)
    
    check_python_version()
    install_requirements()
    setup_environment()
    check_data_file()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your API keys:")
    print("   - GOOGLE_API_KEY (from Google AI Studio)")
    print("   - APIFY_API_TOKEN (from Apify Console)")
    print("2. Run the application: streamlit run app.py")
    print("\n🔗 Useful links:")
    print("- Google AI Studio: https://makersuite.google.com/app/apikey")
    print("- Apify Console: https://console.apify.com/account/integrations")

if __name__ == "__main__":
    main()
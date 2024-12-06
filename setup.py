import subprocess
import sys
import os

def setup_project():
    """Setup the project environment"""
    print("Setting up Bank Check Parser project...")
    
    # Create necessary directories
    directories = ['logs', 'models', 'static', 'uploads']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created {directory} directory")
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("""# Application Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///./checks.db

# OCR Settings
TESSERACT_CMD=tesseract

# API Settings
API_URL=http://localhost:5000
""")
        print("Created .env file")
    
    # Install requirements
    print("Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("\nSetup completed successfully!")
    print("\nTo start the application:")
    print("1. Start the Flask API server:")
    print("   python run.py")
    print("\n2. In a new terminal, start the Streamlit interface:")
    print("   python run_streamlit.py")

if __name__ == "__main__":
    setup_project() 
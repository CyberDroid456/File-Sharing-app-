# install.py - Simple installation script
import os
import subprocess
import sys

def install_dependencies():
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies. Please check your internet connection.")
        return False
    return True

def create_folders():
    print("Creating necessary folders...")
    folders = ["uploads", "logs", "static", "templates"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✅ Created {folder}/ directory")
    
    # Create default shared_links.json if it doesn't exist
    if not os.path.exists("shared_links.json"):
        with open("shared_links.json", "w") as f:
            f.write("{}")
        print("✅ Created shared_links.json")

def check_files():
    print("Checking required files...")
    required_files = ["app.py", "shared_links.py", "config.py"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing files:", ", ".join(missing_files))
        return False
    
    print("✅ All required files found!")
    return True

def check_templates():
    print("Checking template files...")
    required_templates = [
        "index.html", "login.html", "browse.html", "logs.html",
        "my_shares.html", "preview_image.html", "preview_pdf.html",
        "preview_text.html", "share_password.html"
    ]
    
    missing_templates = []
    for template in required_templates:
        if not os.path.exists(os.path.join("templates", template)):
            missing_templates.append(template)
    
    if missing_templates:
        print("❌ Missing templates:", ", ".join(missing_templates))
        return False
    
    print("✅ All template files found!")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("File Share Application Setup")
    print("=" * 50)
    
    if not check_files():
        print("\nPlease make sure all required files are present.")
        sys.exit(1)
    
    if not check_templates():
        print("\nPlease make sure all template files are in the templates folder.")
        sys.exit(1)
    
    if install_dependencies():
        create_folders()
        print("\n🎉 Setup complete! You can now:")
        print("1. Run 'python app.py' to start the server")
        print("2. Run 'python build.py' to create an executable")
        print("3. Edit config.py to customize settings")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
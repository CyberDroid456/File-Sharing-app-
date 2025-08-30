# build.py - Script to build the executable
import os
import sys
import shutil
import subprocess

def build_executable():
    print("🔨 Building File Share executable...")
    
    # Install PyInstaller if not already installed
    try:
        import PyInstaller
        print("✅ PyInstaller is already installed")
    except ImportError:
        print("Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller. Please install it manually:")
            print("   pip install pyinstaller")
            return False
    
    # Create build directory
    build_dir = "build"
    dist_dir = "dist"
    
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    # Create necessary directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Check if required files exist
    required_files = ["app.py", "shared_links.py", "config.py"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Error: '{file}' not found!")
            return False
    
    # Check if static and templates directories exist
    if not os.path.exists("static"):
        print("❌ Error: 'static' directory not found!")
        return False
        
    if not os.path.exists("templates"):
        print("❌ Error: 'templates' directory not found!")
        return False
    
    # Create shared_links.json if it doesn't exist
    if not os.path.exists("shared_links.json"):
        with open("shared_links.json", "w") as f:
            f.write("{}")
        print("✅ Created shared_links.json")
    
    # PyInstaller command - use the Python module directly
    python_executable = sys.executable
    cmd = [
        python_executable,
        "-m", "PyInstaller",
        "--name=FileShare",
        "--onefile",
        "--windowed",  # No console window
        "--add-data", "static;static",
        "--add-data", "templates;templates", 
        "--add-data", "uploads;uploads",
        "--add-data", "logs;logs",
        "--add-data", "config.py;.",
        "--add-data", "shared_links.py;.",
        "--add-data", "shared_links.json;.",
        "--hidden-import=werkzeug.utils",
        "--hidden-import=werkzeug.security",
        "app.py"
    ]
    
    # Add icon if it exists
    if os.path.exists("static/icon.ico"):
        cmd.extend(["--icon", "static/icon.ico"])
    
    print("Running PyInstaller...")
    print("Command:", " ".join(cmd))
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            print("✅ Build successful!")
            print(f"Executable is located in: {os.path.abspath('dist')}")
            
            # Copy necessary files to dist directory
            dist_path = os.path.abspath("dist")
            for folder in ["uploads", "logs"]:
                target_path = os.path.join(dist_path, folder)
                if not os.path.exists(target_path):
                    os.makedirs(target_path)
            
            # Copy config files
            for file in ["config.py", "shared_links.py", "shared_links.json"]:
                if os.path.exists(file):
                    shutil.copy2(file, dist_path)
            
            # Create a simple README for the executable
            readme_content = """File Share Application
=====================

To run the application:
1. Double-click on FileShare.exe
2. Open your web browser
3. Go to http://localhost:5000
4. Login with admin/admin123 or user/user123

Files will be stored in the 'uploads' folder.
Logs will be stored in the 'logs' folder.

Default credentials:
- Admin: admin/admin123
- User: user/user123

Note: The first time you run the application, it may take a few seconds to start.
You can edit config.py to change settings like:
- Maximum file size
- Allowed file types
- User accounts and passwords
- Server port
"""
            
            with open(os.path.join(dist_path, "README.txt"), "w") as f:
                f.write(readme_content)
                
            print("📝 README.txt created with instructions")
            
            # Create a batch file for easy launching
            batch_content = """@echo off
echo ========================================
echo    File Share Application Launcher
echo ========================================
echo.
echo Starting server...
echo.
echo Once started, open your web browser and go to:
echo http://localhost:5000
echo.
echo Default login credentials:
echo Admin: admin/admin123
echo User: user/user123
echo.
echo Press Ctrl+C to stop the server
echo.
FileShare.exe
pause
"""
            
            with open(os.path.join(dist_path, "run.bat"), "w") as f:
                f.write(batch_content)
                
            print("🔄 run.bat created for easy launching")
            return True
            
        else:
            print("❌ Build failed!")
            print("Error output:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Build timed out after 5 minutes")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found. Please make sure it's installed:")
        print("   pip install pyinstaller")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = build_executable()
    if not success:
        sys.exit(1)
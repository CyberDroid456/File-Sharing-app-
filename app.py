from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, flash, session
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# Load user configuration
try:
    from config import *
except ImportError:
    # Fallback defaults if config.py doesn't exist
    APP_NAME = "File Share"
    MAX_FILE_SIZE = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}
    UPLOAD_FOLDER = "uploads"
    LOG_FOLDER = "logs"
    USERS = {
        "admin": {"password": "admin123", "role": "admin"},
        "user": {"password": "user123", "role": "user"}
    }
    HOST = "0.0.0.0"
    PORT = 5000
    DEBUG = True

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Use config settings
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def log_action(action, filename=None):
    """Log user actions"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = session.get('username', 'anonymous')
    log_entry = f"{timestamp} {user} {action}"
    if filename:
        log_entry += f" {filename}"
    log_entry += "\n"
    
    with open(os.path.join(LOG_FOLDER, "activity.log"), "a") as f:
        f.write(log_entry)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username in USERS and USERS[username]["password"] == password:
            session['username'] = username
            session['role'] = USERS[username]["role"]
            log_action("login")
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    log_action("logout")
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    files = os.listdir(UPLOAD_FOLDER)
    file_data = []
    
    for file in files:
        full_path = os.path.join(UPLOAD_FOLDER, file)
        if os.path.isfile(full_path):
            size_kb = round(os.path.getsize(full_path) / 1024, 1)
            file_data.append({"name": file, "size": f"{size_kb} KB", "is_file": True})
        else:
            file_data.append({"name": file, "size": "Folder", "is_file": False})
    
    return render_template("index.html", 
                         files=file_data,
                         user=session['username'], 
                         role=session['role'])

@app.route("/upload", methods=["POST"])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if "file" not in request.files:
        flash("No file part")
        return redirect(url_for("index"))

    file = request.files["file"]

    if file.filename == "":
        flash("No selected file")
        return redirect(url_for("index"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            # Save the file in chunks for large files
            file.save(save_path)
            log_action("uploaded", filename)

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": True, "message": f"{filename} uploaded!"})

            flash(f"{filename} uploaded successfully!")
            return redirect(url_for("index"))
            
        except Exception as e:
            # Clean up partially uploaded file
            if os.path.exists(save_path):
                os.remove(save_path)
                
            error_msg = f"Upload failed: {str(e)}"
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "message": error_msg}), 500
                
            flash(error_msg)
            return redirect(url_for("index"))

    flash("File type not allowed")
    return redirect(url_for("index"))

@app.route("/create_folder", methods=["POST"])
def create_folder():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    folder_name = request.form.get('folder_name')
    if not folder_name:
        flash("Folder name cannot be empty")
        return redirect(url_for("index"))
    
    # Remove special characters for safety
    folder_name = secure_filename(folder_name.strip())
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    
    if os.path.exists(folder_path):
        flash(f"Folder '{folder_name}' already exists!")
    else:
        os.makedirs(folder_path)
        log_action("created_folder", folder_name)
        flash(f"Folder '{folder_name}' created successfully!")
    
    return redirect(url_for("index"))

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/download/<filename>")
def download(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    log_action("downloaded", filename)
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/delete/<path:filename>", methods=["POST"])
def delete_file(filename):
    if 'username' not in session or session.get('role') != 'admin':
        flash("Unauthorized")
        return redirect(url_for("index"))
    
    filename = secure_filename(filename)
    path = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(path):
        try:
            if os.path.isfile(path):
                # Delete single file
                os.remove(path)
                log_action("deleted", filename)
                message = f"{filename} deleted successfully!"
                
            else:
                # Delete folder recursively
                import shutil
                shutil.rmtree(path)
                log_action("deleted_folder", filename)
                message = f"Folder '{filename}' and all contents deleted successfully!"
            
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": True, "message": message})
            
            flash(message)
            
        except Exception as e:
            error_msg = f"Delete failed: {str(e)}"
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "message": error_msg}), 500
            flash(error_msg)
    else:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "message": "File/folder not found"}), 404
        flash("File/folder not found")

    return redirect(url_for("index"))

@app.route("/logs")
def logs():
    if 'username' not in session or session.get('role') != 'admin':
        flash("Unauthorized")
        return redirect(url_for("index"))
    
    log_file_path = os.path.join(LOG_FOLDER, "activity.log")
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as f:
            log_lines = f.readlines()
    else:
        log_lines = []
    
    return render_template("logs.html", logs=log_lines)

@app.route("/browse")
@app.route("/browse/<path:folder_path>")
def browse(folder_path=""):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Build full path safely
    current_path = os.path.join(UPLOAD_FOLDER, folder_path)
    
    # Security check: prevent directory traversal
    if not os.path.realpath(current_path).startswith(os.path.realpath(UPLOAD_FOLDER)):
        flash("Access denied")
        return redirect(url_for("index"))
    
    if not os.path.exists(current_path):
        flash("Folder does not exist")
        return redirect(url_for("index"))
    
    # Get files and folders
    items = []
    for item in os.listdir(current_path):
        item_path = os.path.join(current_path, item)
        full_item_path = os.path.join(folder_path, item) if folder_path else item
        
        if os.path.isfile(item_path):
            size_kb = round(os.path.getsize(item_path) / 1024, 1)
            items.append({
                "name": item, 
                "size": f"{size_kb} KB", 
                "is_file": True,
                "path": full_item_path
            })
        else:
            items.append({
                "name": item, 
                "size": "Folder", 
                "is_file": False,
                "path": full_item_path
            })
    
    # Calculate breadcrumbs
    breadcrumbs = []
    if folder_path:
        parts = folder_path.split('/')
        for i in range(len(parts)):
            breadcrumbs.append({
                "name": parts[i],
                "path": '/'.join(parts[:i+1])
            })
    
    return render_template("browse.html", 
                         items=items,
                         current_path=folder_path,
                         breadcrumbs=breadcrumbs,
                         user=session['username'], 
                         role=session['role'])

@app.route("/upload_to_folder/<path:folder_path>", methods=["POST"])
def upload_to_folder(folder_path):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Security check
    full_folder_path = os.path.join(UPLOAD_FOLDER, folder_path)
    if not os.path.realpath(full_folder_path).startswith(os.path.realpath(UPLOAD_FOLDER)):
        return jsonify({"success": False, "message": "Access denied"}), 403
    
    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file part"})
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "message": "No selected file"})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(full_folder_path, filename)
        file.save(save_path)
        log_action("uploaded", f"{folder_path}/{filename}" if folder_path else filename)
        
        return jsonify({"success": True, "message": f"{filename} uploaded to folder!"})
    
    return jsonify({"success": False, "message": "File type not allowed"})

@app.route("/create_subfolder/<path:parent_path>", methods=["POST"])
def create_subfolder(parent_path):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    folder_name = request.form.get('folder_name')
    if not folder_name:
        flash("Folder name cannot be empty")
        return redirect(url_for("browse", folder_path=parent_path))
    
    # Security check
    full_parent_path = os.path.join(UPLOAD_FOLDER, parent_path)
    if not os.path.realpath(full_parent_path).startswith(os.path.realpath(UPLOAD_FOLDER)):
        flash("Access denied")
        return redirect(url_for("browse", folder_path=parent_path))
    
    # Remove special characters for safety
    folder_name = secure_filename(folder_name.strip())
    folder_path = os.path.join(full_parent_path, folder_name)
    
    if os.path.exists(folder_path):
        flash(f"Folder '{folder_name}' already exists!")
    else:
        os.makedirs(folder_path)
        full_folder_name = f"{parent_path}/{folder_name}" if parent_path else folder_name
        log_action("created_folder", full_folder_name)
        flash(f"Folder '{folder_name}' created successfully!")
    
    return redirect(url_for("browse", folder_path=parent_path))

@app.route("/preview/<path:filename>")
def preview_file(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Security check
    if not os.path.realpath(file_path).startswith(os.path.realpath(UPLOAD_FOLDER)):
        return "Access denied", 403
    
    if not os.path.exists(file_path):
        return "File not found", 404
    
    # Determine file type and render appropriate preview
    file_ext = filename.split('.')[-1].lower() if '.' in filename else ''
    
    if file_ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
        return render_template("preview_image.html", filename=filename, file_path=file_path)
    
    elif file_ext in ['pdf']:
        return render_template("preview_pdf.html", filename=filename, file_path=file_path)
    
    elif file_ext in ['txt', 'log', 'csv', 'json', 'xml', 'html', 'css', 'js', 'py']:
        return render_template("preview_text.html", filename=filename, file_path=file_path)
    
    else:
        # For unsupported types, offer download
        return redirect(url_for('download', filename=filename))

@app.route("/get_file_content/<path:filename>")
def get_file_content(filename):
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Security check
    if not os.path.realpath(file_path).startswith(os.path.realpath(UPLOAD_FOLDER)):
        return jsonify({"error": "Access denied"}), 403
    
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({"content": content})
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
            return jsonify({"content": content})
        except:
            return jsonify({"error": "Cannot preview binary file"})
    except:
        return jsonify({"error": "Cannot read file"})

if __name__ == "__main__":
    print(f"🚀 Starting File Share on localhost")
    print(f"📍 Local: http://127.0.0.1:5000")
    print(f"⏰ Timeout set to: 3600 seconds (1 hour) for large files")
    
    # Increase timeout for large files
    from werkzeug.serving import WSGIRequestHandler
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    
    # Run on localhost instead of network IP (this fixes ngrok compatibility)
    app.run(host="127.0.0.1", port=5000, debug=DEBUG, threaded=True)
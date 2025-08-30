from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, flash, session
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from shared_links import create_share_link, get_share_link, increment_download_count, delete_share_link, get_user_shared_links, cleanup_expired_links

# Load user configuration
try:
    from config import *
except ImportError:
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

app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def log_action(action, filename=None):
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
        file.save(save_path)
        log_action("uploaded", filename)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": True, "message": f"{filename} uploaded!"})

        flash(f"{filename} uploaded successfully!")
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

@app.route("/delete/<filename>", methods=["POST"])
def delete_file(filename):
    if 'username' not in session or session.get('role') != 'admin':
        flash("Unauthorized")
        return redirect(url_for("index"))
    
    filename = secure_filename(filename)
    path = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
            log_action("deleted", filename)
            message = f"{filename} deleted successfully!"
        else:
            import shutil
            shutil.rmtree(path)
            log_action("deleted_folder", filename)
            message = f"Folder '{filename}' and all contents deleted successfully!"
        
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": True, "message": message})
        
        flash(message)
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

# Shareable links routes
@app.route("/share/<path:filename>", methods=["POST"])
def share_file(filename):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    expires_days = int(request.form.get('expires_days', 7))
    password = request.form.get('password') or None
    
    share_id = create_share_link(filename, session['username'], expires_days, password)
    share_url = f"{request.host_url}s/{share_id}"
    
    return jsonify({
        "success": True, 
        "message": "Share link created!",
        "share_url": share_url,
        "share_id": share_id
    })

@app.route("/s/<share_id>", methods=["GET", "POST"])
def shared_file_access(share_id):
    share_data = get_share_link(share_id)
    
    if not share_data:
        return "Share link not found or expired", 404
    
    # Check expiration
    expires_at = datetime.strptime(share_data["expires_at"], "%Y-%m-%d %H:%M:%S")
    if datetime.now() > expires_at:
        delete_share_link(share_id)
        return "Share link expired", 410
    
    # Password protection check
    if share_data["password"]:
        if request.method == "POST":
            # Check password from form submission
            if request.form.get("password") == share_data["password"]:
                increment_download_count(share_id)
                return send_from_directory(UPLOAD_FOLDER, share_data["file_path"])
            else:
                return render_template("share_password.html", 
                                    share_id=share_id, 
                                    error="Incorrect password")
        else:
            # Show password form for GET requests
            return render_template("share_password.html", share_id=share_id)
    
    # No password required
    increment_download_count(share_id)
    return send_from_directory(UPLOAD_FOLDER, share_data["file_path"])

@app.route("/my-shares")
def my_shares():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user_links = get_user_shared_links(session['username'])
    cleanup_expired_links()
    
    return render_template("my_shares.html", 
                         shares=user_links,
                         user=session['username'], 
                         role=session['role'])

@app.route("/delete-share/<share_id>", methods=["POST"])
def delete_share(share_id):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    share_data = get_share_link(share_id)
    if not share_data or share_data["created_by"] != session['username']:
        return jsonify({"success": False, "message": "Share not found"}), 404
    
    delete_share_link(share_id)
    return jsonify({"success": True, "message": "Share deleted"})

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

# Add this missing route for text file content
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
        return jsonify({"error": "Cannot read file (binary or unsupported encoding)"})
    except Exception as e:
        return jsonify({"error": f"Error reading file: {str(e)}"})

if __name__ == "__main__":
    import socket
    
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    safe_ip = get_local_ip()
    
    print(f"🚀 Starting on SAFE interface: {safe_ip}")
    print(f"📍 Local: http://127.0.0.1:5000")
    print(f"🌐 Network: http://{safe_ip}:5000")
    
    app.run(host=safe_ip, port=5000, debug=DEBUG)
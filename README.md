# 📂 File-Sharing App

A sleek, secure, and modern file-sharing web application built with Flask.  
Features include drag-and-drop uploads, live previews, role-based access, activity logging, and responsive design.

## ✨ Features

- 🚀 **Fast Uploads** – Drag & drop multiple files at once
- 🔒 **Role-Based Access** – Admins and users with controlled permissions
- 👁️ **File Preview** – Images, PDFs, and text files viewable in the browser
- 🔗 **Shareable Links** – Generate secure links with expiration and password protection
- 🔍 **Instant Search** – Find files instantly with smart filtering
- 🌙 **Dark / Light Mode** – Seamless theme switching
- 📱 **Responsive Design** – Works on desktop, tablet, and mobile

## 🖼️ Screenshots

| Upload & Preview | Dark Mode | Shareable Links |
|------------------|-----------|-----------------|
| ![](./assets/Recording%202025-08-28%20234101.gif) | ![](./assets/darkmode.gif) | ![](./assets/share-links.gif) |

## ⚙️ Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
git clone https://github.com/CyberDroid456/File-Sharing-app-.git
cd File-Sharing-app-
pip install -r requirements.txt
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

### Standalone Executable

You can build a standalone executable (no Python required):

```bash
python install.py      # Install dependencies
python build.py        # Build executable
# The executable will be in the 'dist' folder
```

## 🚀 Deployment

- **Local (ngrok):**
  ```bash
  ngrok http 5000
  ```
- **Cloud (Render, Railway, Heroku):**  
  Coming soon

## 🛡️ Security

- Encrypted file handling
- Role-based access control
- Shareable links with expiration and password protection
- Configurable settings in `config.py`

## 📅 Roadmap

- ✅ Shareable links with expiration and password protection
- [ ] Cloud deployment guide
- [ ] End-to-end encryption
- [ ] QR code sharing
- [ ] Mobile-friendly PWA support
- [ ] User registration system
- [ ] File versioning

## 🔗 Shareable Links Feature

Robust shareable links functionality:

- Generate share links for any file with customizable expiration
- Password protection for sensitive files
- Track download counts for each shared link
- Manage your shares from the "My Shares" section
- Admin controls to monitor all shared links

**How to use shareable links:**
1. Click the "Share" button next to any file
2. Choose expiration time (default: 7 days)
3. Optionally set a password
4. Copy the generated link and share it
5. Monitor downloads from "My Shares"

## 🤝 Contributing

Contributions welcome! Open an issue, suggest features, or submit a pull request.

## 📜 License

MIT
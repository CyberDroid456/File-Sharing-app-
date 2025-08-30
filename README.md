# How to Update Your README to Show Shareable Links as Completed

You can update your README.md file to show that shareable links have been implemented by replacing the checkboxes with completed markers. Here's how to update it:

## Updated README.md:

```markdown
# 📂 File-Sharing App

**A sleek, secure, and modern file-sharing web application built with Flask.**
Drag-and-drop uploads, live previews, role-based access, activity logging, and responsive design.

## ✨ Features

* 🚀 **Fast Uploads** – Drag & drop multiple files at once
* 🔒 **Role-Based Access** – Admins, editors, and viewers with controlled permissions
* 👁️ **File Preview** – Images, PDFs, and text files viewable right in the browser
* 🔗 **Shareable Links** – Generate secure links to share files with expiration and password protection
* 🔍 **Instant Search** – Find files instantly with smart filtering
* 🌙 **Dark / Light Mode** – Switch seamlessly between themes
* 📱 **Responsive** – Works on desktop, tablet, and mobile

## 🖼️ Screenshots

### Features Demo

| Upload & Preview | Dark Mode | Shareable Links |
|------------------|-----------|-----------------|
| ![](./assets/Recording%202025-08-28%20234101.gif) | ![](./assets/darkmode.gif) | ![](./assets/share-links.gif) |

## ⚙️ Getting Started

### Prerequisites

* Python 3.8+
* pip (package manager)

### Installation

```bash
git clone https://github.com/CyberDroid456/File-Sharing-app-.git
cd File-Sharing-app-
pip install -r requirements.txt
python app.py
```

Now open [http://localhost:5000](http://localhost:5000) in your browser.

### Standalone Executable

You can also build a standalone executable that doesn't require Python:

```bash
# Install dependencies
python install.py

# Build executable
python build.py

# The executable will be in the 'dist' folder
```

## 🚀 Deployment

* **Local (ngrok)**:

```bash
ngrok http 5000
```

* **Cloud (Render, Railway, Heroku)**: Coming soon in roadmap

## 🛡️ Security

* Encrypted file handling
* Role-based access control
* Shareable links with expiration and password protection
* Configurable settings in `config.py`

## 📅 Roadmap

* ✅ **Shareable links** - Implemented with expiration and password protection
* [ ] Cloud deployment guide
* ✅ **Link expiry + password-protected links** - Fully implemented
* [ ] End-to-end encryption
* [ ] QR code sharing
* [ ] Mobile-friendly PWA support
* [ ] User registration system
* [ ] File versioning

## Shareable Links Feature

The application now includes robust shareable links functionality:

- **Generate share links** for any file with customizable expiration
- **Password protection** for sensitive files
- **Track download counts** for each shared link
- **Manage your shares** from the "My Shares" section
- **Admin controls** to monitor all shared links

### How to use shareable links:
1. Click the "Share" button next to any file
2. Choose expiration time (default: 7 days)
3. Optionally set a password for extra security
4. Copy the generated link and share it with others
5. Monitor downloads from the "My Shares" page

## 🤝 Contributing

Contributions welcome! Open an issue, suggest features, or submit a pull request.

## 📜 License

MIT License © 2025 [CyberDroid456](https://github.com/CyberDroid456)

// Toast Manager
function showToast(message, type = "success") {
    let toast = document.createElement("div");
    toast.className = `toast ${type} show`;
    toast.innerText = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}

// Custom Delete Confirmation Modal
function confirmDelete(file, callback) {
    // Create overlay
    let overlay = document.createElement("div");
    overlay.style.position = "fixed";
    overlay.style.top = "0";
    overlay.style.left = "0";
    overlay.style.width = "100%";
    overlay.style.height = "100%";
    overlay.style.background = "rgba(0,0,0,0.7)";
    overlay.style.display = "flex";
    overlay.style.justifyContent = "center";
    overlay.style.alignItems = "center";
    overlay.style.zIndex = "9999";
    overlay.style.backdropFilter = "blur(5px)";

    // Create modal box
    let modal = document.createElement("div");
    modal.style.background = "white";
    modal.style.padding = "30px";
    modal.style.borderRadius = "15px";
    modal.style.textAlign = "center";
    modal.style.boxShadow = "0 10px 30px rgba(0,0,0,0.3)";
    modal.style.minWidth = "350px";
    modal.style.maxWidth = "500px";
    
    modal.innerHTML = `
        <h3 style="margin: 0 0 20px 0; color: #2d3748; font-size: 1.5rem;">Confirm Delete</h3>
        <p style="margin: 0 0 25px 0; color: #4a5568; font-size: 1.1rem;">
            Are you sure you want to delete <strong style="color: #e53e3e;">${file}</strong>?
        </p>
        <div style="display: flex; justify-content: center; gap: 15px;">
            <button id="confirmNo" style="
                background: #a0aec0;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
                transition: all 0.3s;
            ">Cancel</button>
            <button id="confirmYes" style="
                background: #e53e3e;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
                transition: all 0.3s;
            ">Yes, Delete</button>
        </div>
    `;

    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    // Add hover effects
    const yesBtn = document.getElementById("confirmYes");
    const noBtn = document.getElementById("confirmNo");
    
    yesBtn.onmouseover = () => {
        yesBtn.style.transform = "translateY(-2px)";
        yesBtn.style.boxShadow = "0 4px 12px rgba(229, 62, 62, 0.3)";
    };
    yesBtn.onmouseout = () => {
        yesBtn.style.transform = "translateY(0)";
        yesBtn.style.boxShadow = "none";
    };
    
    noBtn.onmouseover = () => {
        noBtn.style.transform = "translateY(-2px)";
        noBtn.style.boxShadow = "0 4px 12px rgba(160, 174, 192, 0.3)";
    };
    noBtn.onmouseout = () => {
        noBtn.style.transform = "translateY(0)";
        noBtn.style.boxShadow = "none";
    };

    // Handle buttons
    yesBtn.onclick = () => {
        callback(true);
        overlay.remove();
    };
    
    noBtn.onclick = () => {
        callback(false);
        overlay.remove();
    };

    // Close on overlay click
    overlay.onclick = (e) => {
        if (e.target === overlay) {
            callback(false);
            overlay.remove();
        }
    };
}

// Handle delete with AJAX
function handleDelete(file, url) {
    confirmDelete(file, (confirmed) => {
        if (confirmed) {
            fetch(url, { 
                method: "POST",
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message, "success");
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showToast(data.message, "error");
                }
            })
            .catch(() => showToast("Error deleting file", "error"));
        }
    });
}

// Simple search functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('fileSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('.file-table tbody tr');
            
            rows.forEach(row => {
                const filename = row.querySelector('td:first-child').textContent.toLowerCase();
                if (filename.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
});

// Upload with progress and prevention
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('uploadForm');
    const uploadButton = document.getElementById('uploadButton');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    const uploadStatus = document.getElementById('uploadStatus');
    let isUploading = false;

    if (form) {
        form.addEventListener('submit', function(e) {
            if (isUploading) {
                e.preventDefault();
                showToast("Please wait, upload in progress...", "info");
                return;
            }

            const fileInput = document.getElementById('fileInput');
            if (fileInput.files.length === 0) {
                showToast("Please select a file first", "error");
                e.preventDefault();
                return;
            }

            e.preventDefault();
            isUploading = true;
            
            // Show progress and disable button
            uploadProgress.style.display = 'block';
            uploadButton.classList.add('uploading');
            uploadButton.textContent = 'Uploading...';
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            
            const xhr = new XMLHttpRequest();
            
            // Progress tracking
           xhr.addEventListener('load', function() {
    if (xhr.status === 200) {
        try {
            const response = JSON.parse(xhr.responseText);
            if (response.success) {
                showToast(response.message, "success");
                progressBar.style.width = '100%';
                uploadStatus.textContent = 'Upload Complete!';
                
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                showToast(response.message, "error");
                resetUploadUI();
            }
        } catch (e) {
            showToast("Upload completed but server response invalid", "error");
            resetUploadUI();
        }
    } else {
        showToast("Upload failed", "error");
        resetUploadUI();
    }
    isUploading = false;
});
            
            xhr.addEventListener('error', function() {
                showToast("Upload error", "error");
                resetUploadUI();
                isUploading = false;
            });
            
            xhr.open('POST', this.action);
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            xhr.send(formData);
        });
    }

    function resetUploadUI() {
        uploadProgress.style.display = 'none';
        progressBar.style.width = '0%';
        uploadButton.classList.remove('uploading');
        uploadButton.textContent = 'Upload';
    }
});
// Theme Management
function initTheme() {
    // Get saved theme or use system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
    setTheme(initialTheme);
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateThemeButton(theme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
}

function updateThemeButton(theme) {
    const button = document.getElementById('themeToggle');
    if (button) {
        button.innerHTML = theme === 'dark' ? '☀️' : '🌙';
        button.title = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
    }
}

// Add theme toggle button to page
function addThemeButton() {
    const button = document.createElement('button');
    button.id = 'themeToggle';
    button.className = 'theme-toggle';
    button.innerHTML = '🌙';
    button.title = 'Toggle dark mode';
    button.onclick = toggleTheme;
    document.body.appendChild(button);
}

// Initialize theme when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    addThemeButton();
    
    // Add theme class to body for transitions
    setTimeout(() => {
        document.body.classList.add('theme-loaded');
    }, 100);
});
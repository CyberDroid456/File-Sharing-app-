// Shareable links functionality
let currentSharingFile = null;

function openShareModal(filename) {
    currentSharingFile = filename;
    const modal = document.getElementById('shareModal');
    modal.style.display = 'block';
    
    document.getElementById('expireCheck').checked = true;
    document.getElementById('passwordCheck').checked = false;
    document.getElementById('sharePassword').style.display = 'none';
    document.getElementById('shareLinkInput').value = 'Generating...';
    
    generateShareLink(filename);
}

function closeShareModal() {
    document.getElementById('shareModal').style.display = 'none';
    currentSharingFile = null;
}

function generateShareLink(filename) {
    const expires = document.getElementById('expireCheck').checked;
    const expiresDays = expires ? 7 : 365;
    const usePassword = document.getElementById('passwordCheck').checked;
    const password = document.getElementById('sharePassword').value;
    
    // Validate password if checkbox is checked
    if (usePassword && !password) {
        showToast('Please enter a password', 'error');
        document.getElementById('shareLinkInput').value = 'Please enter password';
        return;
    }
    
    const formData = new FormData();
    formData.append('expires_days', expiresDays);
    if (usePassword) {
        formData.append('password', password);
    }
    
    fetch(`/share/${encodeURIComponent(filename)}`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('shareLinkInput').value = data.share_url;
            showToast('Share link created successfully!', 'success');
        } else {
            showToast('Failed to create share link', 'error');
            document.getElementById('shareLinkInput').value = 'Error generating link';
        }
    })
    .catch(error => {
        showToast('Error creating share link', 'error');
        document.getElementById('shareLinkInput').value = 'Error generating link';
    });
}

// Event listeners for share modal
document.addEventListener('DOMContentLoaded', function() {
    const passwordCheck = document.getElementById('passwordCheck');
    if (passwordCheck) {
        passwordCheck.addEventListener('change', function() {
            document.getElementById('sharePassword').style.display = this.checked ? 'block' : 'none';
        });
    }
    
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('shareModal');
        if (event.target === modal) {
            closeShareModal();
        }
    });
});
function copyShareLink() {
    const shareLinkInput = document.getElementById('shareLinkInput');
    shareLinkInput.select();
    shareLinkInput.setSelectionRange(0, 99999);
    document.execCommand('copy');
    showToast('Share link copied to clipboard!', 'success');
}
function showToast(message, type = "success") {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 400);
    }, 3000);
}

function handleDelete(filename, deleteUrl) {
    if (confirm(`Are you sure you want to delete "${filename}"?`)) {
        fetch(deleteUrl, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, "success");
                setTimeout(() => location.reload(), 1500);
            } else {
                showToast(data.message, "error");
            }
        })
        .catch(error => {
            showToast("Delete failed", "error");
        });
    }
}
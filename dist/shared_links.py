import json
import os
from datetime import datetime, timedelta
import secrets

SHARED_LINKS_FILE = "shared_links.json"

def init_shared_links():
    if not os.path.exists(SHARED_LINKS_FILE):
        with open(SHARED_LINKS_FILE, 'w') as f:
            json.dump({}, f)

def generate_share_id():
    return secrets.token_urlsafe(8)

def create_share_link(file_path, created_by, expires_days=7, password=None):
    init_shared_links()
    
    share_id = generate_share_id()
    expires_at = (datetime.now() + timedelta(days=expires_days)).strftime("%Y-%m-%d %H:%M:%S")
    
    share_data = {
        "file_path": file_path,
        "created_by": created_by,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expires_at": expires_at,
        "password": password,
        "download_count": 0
    }
    
    with open(SHARED_LINKS_FILE, 'r+') as f:
        links = json.load(f)
        links[share_id] = share_data
        f.seek(0)
        json.dump(links, f, indent=2)
    
    return share_id

def get_share_link(share_id):
    init_shared_links()
    
    with open(SHARED_LINKS_FILE, 'r') as f:
        links = json.load(f)
        return links.get(share_id)

def increment_download_count(share_id):
    init_shared_links()
    
    with open(SHARED_LINKS_FILE, 'r+') as f:
        links = json.load(f)
        if share_id in links:
            links[share_id]["download_count"] += 1
            f.seek(0)
            json.dump(links, f, indent=2)

def delete_share_link(share_id):
    init_shared_links()
    
    with open(SHARED_LINKS_FILE, 'r+') as f:
        links = json.load(f)
        if share_id in links:
            del links[share_id]
            f.seek(0)
            f.truncate()
            json.dump(links, f, indent=2)

def get_user_shared_links(username):
    init_shared_links()
    
    with open(SHARED_LINKS_FILE, 'r') as f:
        links = json.load(f)
        return {id: data for id, data in links.items() if data["created_by"] == username}

def cleanup_expired_links():
    init_shared_links()
    
    with open(SHARED_LINKS_FILE, 'r+') as f:
        links = json.load(f)
        current_time = datetime.now()
        
        expired_ids = [
            id for id, data in links.items() 
            if datetime.strptime(data["expires_at"], "%Y-%m-%d %H:%M:%S") < current_time
        ]
        
        for id in expired_ids:
            del links[id]
        
        f.seek(0)
        f.truncate()
        json.dump(links, f, indent=2)
    
    return len(expired_ids)
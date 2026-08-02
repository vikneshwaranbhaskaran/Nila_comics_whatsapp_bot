import os
import requests
import shelve
from flask import current_app
import logging

def get_cached_media_id(filepath):
    """Uploads media to WhatsApp and caches the media_id in shelve to reuse."""
    if not os.path.exists(filepath):
        return None
        
    cache_key = os.path.abspath(filepath)
    
    with shelve.open("media_cache_db") as db:
        cached = db.get(cache_key)
        if cached:
            return cached
            
        logging.info(f"Uploading {filepath} to WhatsApp Media API...")
        
        url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/media"
        headers = {
            "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}"
        }
        
        content_type = "image/jpeg" if filepath.lower().endswith((".jpg", ".jpeg")) else "image/png"
        
        try:
            with open(filepath, "rb") as f:
                files = {
                    "file": (os.path.basename(filepath), f, content_type)
                }
                data = {
                    "messaging_product": "whatsapp"
                }
                response = requests.post(url, headers=headers, files=files, data=data, timeout=20)
                
            response.raise_for_status()
            result = response.json()
            media_id = result.get("id")
            if media_id:
                db[cache_key] = media_id
                logging.info(f"Successfully uploaded {filepath}. Media ID: {media_id}")
                return media_id
        except Exception as e:
            logging.error(f"Failed to upload media {filepath}: {e}")
            if hasattr(e, "response") and e.response is not None:
                logging.error(f"Upload error response: {e.response.text}")
            
        return None

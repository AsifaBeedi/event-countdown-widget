# Firebase Configuration Template
# Copy this file to firebase_config.py and add your Firebase credentials

# To use Firebase cloud sync features:
# 1. Create a Firebase project at https://console.firebase.google.com/
# 2. Enable Firestore Database
# 3. Download your service account key JSON file
# 4. Update the configuration below

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID", "your-project-id"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", ""),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL", ""),
    "client_id": os.getenv("FIREBASE_CLIENT_ID", ""),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL", "")
}

# Firestore collection names
COLLECTIONS = {
    "events": "countdown_events",
    "users": "users",
    "settings": "user_settings"
}

class FirebaseSync:
    """Firebase cloud synchronization (Optional feature)"""
    
    def __init__(self):
        self.enabled = False
        self.db = None
        self.user_id = None
        
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            # Initialize Firebase if credentials are available
            if not firebase_admin._apps:
                cred = credentials.Certificate(FIREBASE_CONFIG)
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            self.enabled = True
            
        except Exception as e:
            print(f"Firebase initialization failed: {e}")
            print("Running in local-only mode.")
    
    def sync_events_to_cloud(self, events):
        """Sync local events to cloud"""
        if not self.enabled or not self.user_id:
            return False
        
        try:
            for event in events:
                doc_ref = self.db.collection(COLLECTIONS["events"]).document(str(event['id']))
                doc_ref.set({
                    'name': event['name'],
                    'description': event['description'],
                    'event_date': event['event_date'],
                    'priority': event['priority'],
                    'notification_enabled': event['notification_enabled'],
                    'notification_days_before': event['notification_days_before'],
                    'user_id': self.user_id,
                    'created_at': event['created_at'],
                    'updated_at': event['updated_at']
                })
            return True
        except Exception as e:
            print(f"Failed to sync events to cloud: {e}")
            return False
    
    def sync_events_from_cloud(self):
        """Sync events from cloud to local"""
        if not self.enabled or not self.user_id:
            return []
        
        try:
            docs = self.db.collection(COLLECTIONS["events"]).where('user_id', '==', self.user_id).stream()
            events = []
            
            for doc in docs:
                data = doc.to_dict()
                events.append(data)
            
            return events
        except Exception as e:
            print(f"Failed to sync events from cloud: {e}")
            return []
    
    def set_user_id(self, user_id):
        """Set the current user ID for cloud sync"""
        self.user_id = user_id

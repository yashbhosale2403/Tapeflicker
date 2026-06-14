import os
import json
import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    """Initialize Firebase Admin SDK dynamically for production or development"""
    if not firebase_admin._apps:
        try:
            # 1. Primary path: Load certificate JSON from environment variable
            firebase_key_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
            if firebase_key_json:
                try:
                    cred_info = json.loads(firebase_key_json)
                    cred = credentials.Certificate(cred_info)
                    firebase_admin.initialize_app(cred)
                    print("Firebase Admin SDK initialized dynamically from environment credentials.")
                    return
                except Exception as json_err:
                    print(f"ERROR parsing FIREBASE_SERVICE_ACCOUNT_JSON env var: {json_err}")
            
            # 2. Secondary path: Fallback to local service account key file in project root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            key_path = os.path.join(base_dir, 'tapeflicker-10701-firebase-adminsdk-fbsvc-eb802cb2eb.json')
            
            if os.path.exists(key_path):
                cred = credentials.Certificate(key_path)
                firebase_admin.initialize_app(cred)
                print("Firebase Admin SDK initialized from root key file.")
            else:
                print("WARNING: Firebase credentials environment variable or local key file not found. Firebase features will fail.")
        except Exception as e:
            print(f"ERROR initializing Firebase Admin SDK: {e}")

# Call it immediately when imported
initialize_firebase()

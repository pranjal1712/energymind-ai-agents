import os
import asyncio
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Paths
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'token.json')
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'users_backup.db')

# Full drive scope so it can see user-created folders
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print("\n[ERROR] credentials.json not found! Cannot start Google Drive Backup.\n")
                return None
            print("\n" + "="*60)
            print("🚀 FIRST TIME SETUP: GOOGLE DRIVE AUTHORIZATION REQUIRED")
            print("="*60)
            print("A browser window should open automatically to ask for permission.")
            print("If it does not open, please look for a link below and click it.")
            print("Login with your Google account and click 'Continue'.\n")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    try:
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"ERROR building Drive Service: {e}")
        return None

def is_db_empty():
    import sqlite3
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        count = cur.fetchone()[0]
        conn.close()
        return count == 0
    except:
        return True

def upload_backup_to_drive():
    folder_id = os.getenv("GDRIVE_FOLDER_ID")
    if not folder_id:
        print("ERROR: GDRIVE_FOLDER_ID is not set in .env. Cannot upload to Drive.")
        return

    if not os.path.exists(DB_FILE):
        print("DEBUG: No local backup file found to upload yet.")
        return

    service = get_drive_service()
    if not service: return

    file_name = "users_backup.db"

    try:
        # Search for existing backup file in the folder to overwrite it
        query = f"'{folder_id}' in parents and name='{file_name}' and trashed=false"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])

        media = MediaFileUpload(DB_FILE, mimetype='application/x-sqlite3', resumable=True)

        if not items:
            # File doesn't exist, upload a new one
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f"DEBUG: Created new backup on Google Drive. File ID: {file.get('id')}")
        else:
            # File exists, update it to save space (Overwrite)
            file_id = items[0]['id']
            file = service.files().update(fileId=file_id, media_body=media).execute()
            print(f"DEBUG: Successfully updated existing backup on Google Drive (Storage Quota bypassed!).")
            
    except Exception as e:
        print(f"ERROR: Failed to upload backup to Google Drive: {e}")

async def periodic_gdrive_backup():
    # Wait 5 seconds after server startup before the first check
    await asyncio.sleep(5)
    
    # Initialize connection immediately to trigger the browser login if it's the first time
    # We do this outside the loop so the server admin can see it immediately
    get_drive_service()
    
    while True:
        try:
            upload_backup_to_drive()
        except Exception as e:
            print(f"ERROR in periodic GDrive backup loop: {e}")
        # Run exactly every 30 minutes (1800 seconds)
        await asyncio.sleep(1800)

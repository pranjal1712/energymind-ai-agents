import sys
import os

# Ensure the backend module can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine as primary_engine, User, ChatHistory, KnowledgeBase, SessionLocal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def restore_from_backup():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'users_backup.db')
    
    print("=" * 50)
    print("   ENERGYMIND - DISASTER RECOVERY RESTORE TOOL")
    print("=" * 50)
    
    if not os.path.exists(db_path):
        print(f"\n[ERROR] Backup file not found at: {db_path}")
        print("ACTION REQUIRED:")
        print("1. Download 'users_backup.db' from your Google Drive.")
        print("2. Place the file inside the main 'energymind' folder.")
        print("3. Run this script again.")
        return

    # Connect to the downloaded SQLite backup DB
    backup_engine = create_engine(f"sqlite:///{db_path}")
    BackupSession = sessionmaker(bind=backup_engine)
    backup_db = BackupSession()

    # Connect to primary Neon DB
    primary_db = SessionLocal()

    print("\n[INFO] Connected to both databases. Starting data restoration...\n")
    try:
        # Restore Users
        users = backup_db.query(User).all()
        print(f"-> Found {len(users)} users in backup. Restoring...")
        for u in users:
            primary_db.merge(u)
        
        # Restore Chats
        chats = backup_db.query(ChatHistory).all()
        print(f"-> Found {len(chats)} chats in backup. Restoring...")
        for c in chats:
            primary_db.merge(c)
            
        # Restore Knowledge Base
        kbs = backup_db.query(KnowledgeBase).all()
        print(f"-> Found {len(kbs)} KB entries in backup. Restoring...")
        for kb in kbs:
            primary_db.merge(kb)
            
        # Push changes to Neon DB
        primary_db.commit()
        print("\n[SUCCESS] 🎉 All data has been perfectly restored to Neon DB!")
    except Exception as e:
        primary_db.rollback()
        print(f"\n[ERROR] Restoration failed: {e}")
    finally:
        backup_db.close()
        primary_db.close()

if __name__ == "__main__":
    restore_from_backup()

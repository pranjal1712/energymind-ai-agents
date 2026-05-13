import os
from sqlalchemy import text
from backend.database import engine, backup_engine, User, ChatHistory, KnowledgeBase, SessionLocal, BackupSessionLocal

def rebuild_sqlite_from_neon():
    """
    Fetches all data from the primary Neon DB (PostgreSQL) and completely rebuilds 
    the local SQLite database (users_backup.db).
    This only runs in production (Render) to avoid overwriting local developer data.
    """
    if not os.environ.get("RENDER"):
        print("DEBUG: Not running on Render. Skipping Neon-to-SQLite rebuild to protect local DB.")
        return

    print("\n" + "="*50)
    print("🔄 RENDER STARTUP: Rebuilding Local SQLite from Neon DB")
    print("="*50)

    neon_db = SessionLocal()
    backup_db = BackupSessionLocal()

    try:
        # Data will be fetched in batches during Step 3 to save memory.


        # Step 2: Clear existing data in local SQLite (to prevent duplicates)
        backup_db.execute(text("DELETE FROM chat_history"))
        backup_db.execute(text("DELETE FROM knowledge_base"))
        backup_db.execute(text("DELETE FROM users"))
        backup_db.commit()

        # Step 3: Insert everything into local SQLite (Iterate to save RAM)
        print("Migrating Users...")
        for u in neon_db.query(User).yield_per(10):
            backup_db.merge(u)
        
        print("Migrating Chat History...")
        for c in neon_db.query(ChatHistory).yield_per(20):
            backup_db.merge(c)
        
        print("Migrating Knowledge Base...")
        for k in neon_db.query(KnowledgeBase).yield_per(10):
            backup_db.merge(k)
        
        backup_db.commit()
        print("✅ Local SQLite successfully rebuilt from Neon DB!")

    except Exception as e:
        backup_db.rollback()
        print(f"❌ ERROR rebuilding SQLite from Neon: {e}")
    finally:
        neon_db.close()
        backup_db.close()

if __name__ == "__main__":
    rebuild_sqlite_from_neon()

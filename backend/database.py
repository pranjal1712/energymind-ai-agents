from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Create SQLite/PostgreSQL database connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")

# Fix for Supabase/Render postgres URI format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Remove pgbouncer parameter if present (not supported by psycopg2)
if "?pgbouncer=true" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("?pgbouncer=true", "")
elif "&pgbouncer=true" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("&pgbouncer=true", "")

# SQLite needs check_same_thread: False, but Postgres doesn't
is_sqlite = DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {
    "sslmode": "require"
}

# Create engine with pool_pre_ping to refresh stale connections
engine = create_engine(
    DATABASE_URL, 
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- LOCAL BACKUP DB ---
BACKUP_URL = "sqlite:///./users_backup.db"
backup_engine = create_engine(BACKUP_URL, connect_args={"check_same_thread": False})
BackupSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=backup_engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    chats_count = Column(Integer, default=0)
    limit_reached_at = Column(DateTime, nullable=True)
    is_verified = Column(Integer, default=0) # 0 for False, 1 for True
    verification_token = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    lockout_until = Column(DateTime, nullable=True)
    
    chats = relationship("ChatHistory", back_populates="owner")

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="chats")

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, unique=True, index=True)
    slug = Column(String, index=True)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    Base.metadata.create_all(bind=backup_engine)

    # Safely add new columns using IF NOT EXISTS (works on PostgreSQL & SQLite 3.35+)
    migrations = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_token VARCHAR",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMP",
    ]

    # SQLite does NOT support IF NOT EXISTS for ALTER TABLE, use try/except instead
    if is_sqlite:
        with engine.connect() as conn:
            for sql in migrations:
                # Convert to SQLite-compatible syntax (remove IF NOT EXISTS)
                sqlite_sql = sql.replace(" IF NOT EXISTS", "")
                try:
                    conn.execute(text(sqlite_sql))
                    conn.commit()
                except Exception:
                    conn.rollback()
    else:
        # PostgreSQL - IF NOT EXISTS works perfectly
        with engine.connect() as conn:
            for sql in migrations:
                conn.execute(text(sql))
            conn.commit()



def get_db():
    db = SessionLocal()
    db_to_yield = db
    try:
        # Check connection. If Neon DB is down, this will throw an exception.
        db.execute(text("SELECT 1"))
    except Exception as e:
        print(f"WARNING: Primary DB failed ({e}). Falling back to Local Backup DB!")
        db.close()
        db_to_yield = BackupSessionLocal()
        
    try:
        yield db_to_yield
    finally:
        try:
            db_to_yield.close()
        except:
            pass

def sync_to_local(obj):
    """Sync a single SQLAlchemy object to the local backup database in real-time."""
    backup_db = BackupSessionLocal()
    try:
        backup_db.merge(obj)
        backup_db.commit()
    except Exception as e:
        backup_db.rollback()
        print(f"ERROR: Failed to sync object to local DB: {e}")
    finally:
        backup_db.close()

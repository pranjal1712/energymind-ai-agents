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
    
    # Add columns if they do not exist
    try:
        with engine.connect() as conn:
            # PostgreSQL requires rollback on failed queries within a connection
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0"))
                conn.commit()
            except Exception:
                conn.rollback()
            
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN verification_token VARCHAR"))
                conn.commit()
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN reset_token VARCHAR"))
                conn.commit()
            except Exception:
                conn.rollback()
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP"))
                conn.commit()
            except Exception:
                conn.rollback()
    except Exception as e:
        print(f"Error updating schema: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
import re
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

def slugify(text: str) -> str:
    """Helper to create URL-safe slugs from text."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

from .models import ResearchRequest, ResearchResponse
from .research_chain import run_full_research
from .database import engine, Base, get_db, User, ChatHistory, KnowledgeBase, init_db
from .auth import verify_password, get_password_hash, create_access_token, decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_google_token

# Load env variables
load_dotenv()

# Initialize Database
# ... (imports)

# Initialize Database
init_db()

app = FastAPI(title="Autonomous Energy Researcher API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Allow optional auth for guest mode
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Pydantic Models for Auth
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class GoogleAuthRequest(BaseModel):
    token: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str

class UserResponse(BaseModel):
    username: str
    email: str

class ChatHistoryResponse(BaseModel):
    id: int
    query: str
    response: str
    timestamp: datetime

# =========================
# Dependency: Get Current User
# =========================
async def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Helper for optional user
async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token or token == "undefined" or token == "null":
        return None
    try:
        payload = decode_access_token(token)
        if not payload:
            return None
        username: str = payload.get("sub")
        if not username:
            return None
        return db.query(User).filter(User.username == username).first()
    except Exception as e:
        print(f"Auth Error: {e}")
        return None

# =========================
# Auth Routes
# =========================
@app.post("/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = get_password_hash(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "username": new_user.username}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Check both username and email
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "username": user.username}

@app.post("/auth/google", response_model=Token)
async def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    idinfo = verify_google_token(request.token)
    if not idinfo:
        raise HTTPException(status_code=400, detail="Invalid Google token")
    
    email = idinfo.get("email")
    name = idinfo.get("name", email.split('@')[0])
    
    # Check if user exists
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Create new user
        # Generate a unique username from email
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1
            
        user = User(username=username, email=email, hashed_password="GOOGLE_AUTH")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "username": user.username}

@app.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "email": current_user.email}

# =========================
# Research Routes
# =========================
@app.post("/research", response_model=ResearchResponse)
async def run_research_endpoint(
    request: ResearchRequest, 
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    try:
        now = datetime.utcnow()
        
        # 🔹 Quota Enforcement for authenticated users
        if user:
            # Check if 24h reset is needed
            if user.limit_reached_at:
                time_passed = now - user.limit_reached_at
                if time_passed >= timedelta(hours=24):
                    user.chats_count = 0
                    user.limit_reached_at = None
                    db.commit()
                else:
                    remaining = timedelta(hours=24) - time_passed
                    hours, remainder = divmod(remaining.seconds, 3600)
                    minutes = remainder // 60
                    raise HTTPException(
                        status_code=429, 
                        detail=f"Daily limit (15 chats) exceeded. Please try again in {hours}h {minutes}m."
                    )
            
            # Check if limit just hit
            if user.chats_count >= 15:
                user.limit_reached_at = now
                db.commit()
                raise HTTPException(
                    status_code=429, 
                    detail="Daily limit (15 chats) reached. Access will reset in 24 hours."
                )

        # 🔹 check in cache (Knowledge Base DB)
        cached_data = check_in_cache(request.query, db)
        
        is_new_research = False
        if cached_data:
            result_text = cached_data["result"]
            file_path = "Served from Database Cache"
            suggestions = []
        else:
            # 🔹 Run LangChain research with optional thread_id
            research_output = await run_full_research(request.query, request.thread_id)
            result_text = research_output["report"]
            suggestions = research_output.get("suggestions", [])
            is_new_research = True

            # 🔹 Save to knowledge_base (DB)
            save_to_knowledge_base(request.query, result_text, db)
            # 🔹 Save to file as backup
            file_path = save_result_to_file(request.query, result_text)

        # 🔹 Update User Stats & history if authenticated
        if user:
            if is_new_research:
                user.chats_count += 1
            
            chat_entry = ChatHistory(
                user_id=user.id,
                query=request.query,
                response=result_text
            )
            db.add(chat_entry)
            db.commit()

        return ResearchResponse(
            query=request.query,
            result=result_text,
            file_path=file_path,
            suggestions=suggestions
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# History Routes
# =========================
@app.get("/history", response_model=List[ChatHistoryResponse])
async def get_user_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chats = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id)\
              .order_by(ChatHistory.timestamp.desc()).limit(10).all()
    return [{"id": c.id, "query": c.query, "response": c.response, "timestamp": c.timestamp} for c in chats]

@app.delete("/history/{chat_id}")
async def delete_chat_history(chat_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = db.query(ChatHistory).filter(ChatHistory.id == chat_id, ChatHistory.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    db.delete(chat)
    db.commit()
    return {"status": "success", "message": "Chat deleted"}

# Helper to save to file (keeping existing functionality)
def save_result_to_file(query: str, result: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    kb_dir = os.path.join(base_dir, "knowledge_base")
    os.makedirs(kb_dir, exist_ok=True)

    filename = f"{slugify(query)}.txt"
    file_path = os.path.join(kb_dir, filename)

    content = f"""
Query: {query}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

--------------------------------------

{result}
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content.strip())

    return file_path

def save_to_knowledge_base(query: str, content: str, db: Session):
    try:
        slug = slugify(query)
        # Check if exists (shouldn't if check_in_cache was called, but safety first)
        existing = db.query(KnowledgeBase).filter(KnowledgeBase.slug == slug).first()
        if not existing:
            kb_entry = KnowledgeBase(
                query=query,
                slug=slug,
                content=content
            )
            db.add(kb_entry)
            db.commit()
    except Exception as e:
        print(f"Error saving to KB DB: {e}")

def check_in_cache(query: str, db: Session):
    """
    Check if the query result already exists in the knowledge base DB.
    Returns dict with result if found, else None.
    """
    try:
        slug = slugify(query)
        kb_entry = db.query(KnowledgeBase).filter(KnowledgeBase.slug == slug).first()
        
        if kb_entry:
            return {
                "result": kb_entry.content,
                "file_path": "db"
            }
    except Exception as e:
        print(f"Error reading cache from DB: {e}")
        return None
            
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

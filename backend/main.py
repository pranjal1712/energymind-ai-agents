from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
import re
import secrets
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

# Load env variables at the very beginning
load_dotenv()

from .models import ResearchRequest, ResearchResponse
from .research_chain import run_full_research
from .database import engine, Base, get_db, User, ChatHistory, KnowledgeBase, init_db
from .auth import verify_password, get_password_hash, create_access_token, decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_google_token
from .email_service import send_verification_email, send_reset_email

# Helper functions
def slugify(text: str) -> str:
    """Helper to create URL-safe slugs from text."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

def normalize_query(query: str) -> str:
    """Normalize query for fuzzy caching by sorting words."""
    query = query.lower().strip()
    query = re.sub(r'[^\w\s]', '', query)
    words = sorted(query.split())
    return " ".join(words)

# Global RPM tracking
REQUEST_TIMESTAMPS = []
RPM_LIMIT = 25 # Max 25 research requests per minute globally

# App Initialization
app = FastAPI(title="Autonomous Energy Researcher API")

@app.on_event("startup")
async def startup_event():
    print("Initializing Database...")
    try:
        init_db()
        print("Database Initialized Successfully")
    except Exception as e:
        print(f"Database Initialization Failed: {e}")

@app.middleware("http")
async def manual_cors_and_headers(request, call_next):
    origin = request.headers.get("Origin")
    method = request.method
    
    if method == "OPTIONS":
        from fastapi.responses import Response
        resp_origin = origin or "*"
        response = Response(status_code=204)
        response.headers["Access-Control-Allow-Origin"] = resp_origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, X-Requested-With, Origin, DNT, Keep-Alive, User-Agent"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response

    try:
        response = await call_next(request)
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
            headers={"Access-Control-Allow-Origin": origin or "*", "Access-Control-Allow-Credentials": "true"}
        )
    
    response.headers["Access-Control-Allow-Origin"] = origin or "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, X-Requested-With, Origin, DNT, Keep-Alive, User-Agent"
    return response

# Auth dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class GoogleAuthRequest(BaseModel):
    token: str

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

# Auth helpers
async def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token or token in ["undefined", "null"]:
        return None
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        return db.query(User).filter(User.username == username).first()
    except:
        return None

# Routes
@app.post("/signup")
def signup(user: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username taken")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email registered")
    
    otp = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    new_user = User(username=user.username, email=user.email, hashed_password=get_password_hash(user.password), verification_token=otp)
    db.add(new_user)
    db.commit()
    background_tasks.add_task(send_verification_email, user.email, otp, user.username)
    return {"message": "OTP sent to email"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter((User.username == form_data.username) | (User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=401, detail="Verify email first")
    
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "username": user.username}

@app.post("/auth/google", response_model=Token)
async def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    info = verify_google_token(request.token)
    if not info: raise HTTPException(status_code=400, detail="Invalid token")
    email = info.get("email")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(username=email.split('@')[0], email=email, hashed_password="GOOGLE_AUTH", is_verified=1)
        db.add(user)
        db.commit()
        db.refresh(user)
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "username": user.username}

@app.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return {"username": user.username, "email": user.email}

class VerifyOtpRequest(BaseModel):
    email: str
    otp: str

@app.post("/verify-otp")
def verify_otp(req: VerifyOtpRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or user.verification_token != req.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    user.is_verified = 1
    user.verification_token = None
    db.commit()
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "username": user.username, "email": user.email}

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@app.post("/forgot-password")
def forgot(req: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if user:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        background_tasks.add_task(send_reset_email, user.email, token, user.username)
    return {"message": "Reset link sent if email exists"}

@app.post("/reset-password")
def reset(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == req.token).first()
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid token")
    user.hashed_password = get_password_hash(req.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    return {"message": "Password reset success"}

@app.post("/research", response_model=ResearchResponse)
async def research(req: ResearchRequest, user: Optional[User] = Depends(get_optional_user), db: Session = Depends(get_db)):
    try:
        global REQUEST_TIMESTAMPS
        now = datetime.utcnow()
        REQUEST_TIMESTAMPS = [t for t in REQUEST_TIMESTAMPS if now - t < timedelta(seconds=60)]
        if len(REQUEST_TIMESTAMPS) >= RPM_LIMIT:
            raise HTTPException(status_code=429, detail="Server busy, wait 30s")
        REQUEST_TIMESTAMPS.append(now)

        if user:
            if user.limit_reached_at and now - user.limit_reached_at < timedelta(hours=24):
                raise HTTPException(status_code=429, detail="Daily limit reached")
            if user.chats_count >= 15:
                user.limit_reached_at = now
                db.commit()
                raise HTTPException(status_code=429, detail="Daily limit hit")

        norm_q = normalize_query(req.query)
        cache = check_in_cache(norm_q, db)
        if cache:
            return ResearchResponse(query=req.query, result=cache["result"], file_path="cache", suggestions=[])

        output = await run_full_research(req.query, req.thread_id)
        res_text = output["report"]
        save_to_knowledge_base(req.query, res_text, db)
        file_path = save_result_to_file(req.query, res_text)

        if user:
            user.chats_count += 1
            db.add(ChatHistory(user_id=user.id, query=req.query, response=res_text))
            db.commit()

        return ResearchResponse(query=req.query, result=res_text, file_path=file_path, suggestions=output.get("suggestions", []))
    except HTTPException as he: raise he
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/history", response_model=List[ChatHistoryResponse])
async def history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chats = db.query(ChatHistory).filter(ChatHistory.user_id == user.id).order_by(ChatHistory.timestamp.desc()).limit(10).all()
    return chats

@app.delete("/history/{id}")
async def delete_history(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = db.query(ChatHistory).filter(ChatHistory.id == id, ChatHistory.user_id == user.id).first()
    if chat:
        db.delete(chat)
        db.commit()
    return {"message": "Deleted"}

def check_in_cache(query: str, db: Session):
    slug = slugify(normalize_query(query))
    entry = db.query(KnowledgeBase).filter(KnowledgeBase.slug == slug).first()
    return {"result": entry.content} if entry else None

def save_to_knowledge_base(query: str, content: str, db: Session):
    slug = slugify(normalize_query(query))
    if not db.query(KnowledgeBase).filter(KnowledgeBase.slug == slug).first():
        db.add(KnowledgeBase(query=query, slug=slug, content=content))
        db.commit()

def save_result_to_file(query: str, result: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "knowledge_base", f"{slugify(query)}.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: f.write(result)
    return path

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

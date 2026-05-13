from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks, Request
import sentry_sdk
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv
import os
import re
import secrets
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

# Load env variables
load_dotenv()

# --- MODELS ---
class ResearchRequest(BaseModel):
    query: str
    thread_id: Optional[str] = None

class ResearchResponse(BaseModel):
    query: str
    result: str
    id: Optional[int] = None
    file_path: Optional[str] = None
    suggestions: List[str] = []

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class GoogleAuthRequest(BaseModel):
    token: str

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
    username: str

class RefreshRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    username: str
    email: str

class ChatHistoryResponse(BaseModel):
    id: int
    query: str
    response: str
    timestamp: datetime

class VerifyOtpRequest(BaseModel):
    email: str
    otp: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# --- DB & SERVICES ---
from .research_chain import run_full_research
from .database import engine, Base, get_db, User, ChatHistory, KnowledgeBase, init_db, sync_to_local
from .auth import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_google_token
from .email_service import send_verification_email, send_reset_email

# --- HELPERS ---
def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

def normalize_query(query: str) -> str:
    query = query.lower().strip()
    query = re.sub(r'[^\w\s]', '', query)
    words = sorted(query.split())
    return " ".join(words)

REQUEST_TIMESTAMPS = []
IP_REQUESTS = {} # {ip: [timestamps]}
RPM_LIMIT = 25 
IP_RPM_LIMIT = 10 # 10 requests per minute per IP

# --- SENTRY SETUP ---
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        send_default_pii=True
    )
    print("DEBUG: Sentry initialized in backend")

app = FastAPI(title="Autonomous Energy Researcher API")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://energymind-research-ai.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_db()
    from .neon_to_sqlite import rebuild_sqlite_from_neon
    # Rebuild local SQLite from Neon DB (only runs on Render)
    rebuild_sqlite_from_neon()
    
    from .gdrive_backup import periodic_gdrive_backup
    import asyncio
    asyncio.create_task(periodic_gdrive_backup())

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    health_status = {"status": "healthy", "primary_db": "connected", "backup_db": "connected"}
    
    # 1. Check Primary (Neon) directly
    try:
        from .database import SessionLocal
        test_db = SessionLocal()
        test_db.execute(text("SELECT 1"))
        test_db.close()
    except Exception as e:
        health_status["primary_db"] = f"failed: {str(e)}"
        health_status["status"] = "degraded"

    # 2. Check Backup (SQLite)
    try:
        from .database import BackupSessionLocal
        test_backup = BackupSessionLocal()
        test_backup.execute(text("SELECT 1"))
        test_backup.close()
    except Exception as e:
        health_status["backup_db"] = f"failed: {str(e)}"
        if health_status["status"] == "healthy":
            health_status["status"] = "degraded"

    return health_status

@app.middleware("http")
async def manual_cors_and_headers(request, call_next):
    origin = request.headers.get("Origin")
    method = request.method
    if method == "OPTIONS":
        from fastapi.responses import Response
        response = Response(status_code=204)
        response.headers["Access-Control-Allow-Origin"] = origin or "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = origin or "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

async def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token: raise HTTPException(status_code=401)
    payload = decode_access_token(token)
    if not payload: raise HTTPException(status_code=401)
    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if not user: raise HTTPException(status_code=401)
    return user

async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token or token in ["undefined", "null"]: return None
    try:
        payload = decode_access_token(token)
        return db.query(User).filter(User.username == payload.get("sub")).first()
    except: return None

# --- ROUTES ---
@app.post("/signup")
def signup(user: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first(): raise HTTPException(status_code=400, detail="Email exists")
    otp = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    new_user = User(username=user.username, email=user.email, hashed_password=get_password_hash(user.password), verification_token=otp)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    sync_to_local(new_user)
    background_tasks.add_task(send_verification_email, user.email, otp, user.username)
    return {"message": "OTP sent"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter((User.username == form_data.username) | (User.email == form_data.username)).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Check if account is locked
    now = datetime.utcnow()
    if user.lockout_until and user.lockout_until > now:
        remaining_time = int((user.lockout_until - now).total_seconds() / 60)
        raise HTTPException(
            status_code=403, 
            detail=f"Account locked due to too many failed attempts. Try again in {remaining_time} minutes."
        )

    if not verify_password(form_data.password, user.hashed_password):
        # Increment failed attempts
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.lockout_until = now + timedelta(minutes=30)
            db.commit()
            sync_to_local(user)
            raise HTTPException(
                status_code=403, 
                detail="Too many failed attempts. Account locked for 30 minutes."
            )
        db.commit()
        sync_to_local(user)
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Success: Reset attempts
    user.failed_login_attempts = 0
    user.lockout_until = None
    db.commit()
    db.refresh(user)
    sync_to_local(user)

    return {
        "access_token": create_access_token(data={"sub": user.username}),
        "refresh_token": create_refresh_token(data={"sub": user.username}),
        "token_type": "bearer",
        "username": user.username
    }

@app.post("/verify-otp")
def verify_otp(req: VerifyOtpRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or user.verification_token != req.otp: raise HTTPException(status_code=400)
    user.is_verified = 1
    user.verification_token = None
    db.commit()
    db.refresh(user)
    sync_to_local(user)
    return {
        "access_token": create_access_token(data={"sub": user.username}),
        "refresh_token": create_refresh_token(data={"sub": user.username}),
        "token_type": "bearer",
        "username": user.username
    }

@app.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return user

@app.post("/auth/google", response_model=Token)
async def google_auth(req: GoogleAuthRequest, db: Session = Depends(get_db)):
    idinfo = verify_google_token(req.token)
    if not idinfo:
        raise HTTPException(status_code=400, detail="Invalid Google token")
    
    email = idinfo['email']
    username = idinfo.get('name', email.split('@')[0])
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Create new user for Google login if not exists
        user = User(username=username, email=email, hashed_password="google-auth-user", is_verified=1)
        db.add(user)
        db.commit()
        db.refresh(user)
        sync_to_local(user)
    
    return {
        "access_token": create_access_token(data={"sub": user.username}),
        "refresh_token": create_refresh_token(data={"sub": user.username}),
        "token_type": "bearer",
        "username": user.username
    }

@app.post("/refresh", response_model=Token)
def refresh_token(req: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_access_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    return {
        "access_token": create_access_token(data={"sub": user.username}),
        "refresh_token": create_refresh_token(data={"sub": user.username}),
        "token_type": "bearer",
        "username": user.username
    }

@app.post("/research", response_model=ResearchResponse)
async def research(req: ResearchRequest, request: Request, user: Optional[User] = Depends(get_optional_user), db: Session = Depends(get_db)):
    try:
        global REQUEST_TIMESTAMPS, IP_REQUESTS
        now = datetime.utcnow()
        client_ip = request.client.host

        # 1. Global Rate Limit Check
        REQUEST_TIMESTAMPS = [t for t in REQUEST_TIMESTAMPS if now - t < timedelta(seconds=60)]
        if len(REQUEST_TIMESTAMPS) >= RPM_LIMIT: 
            raise HTTPException(status_code=429, detail="Server busy, try again in a minute")

        # 2. IP-based Rate Limit Check
        if client_ip not in IP_REQUESTS:
            IP_REQUESTS[client_ip] = []
        IP_REQUESTS[client_ip] = [t for t in IP_REQUESTS[client_ip] if now - t < timedelta(seconds=60)]
        
        if len(IP_REQUESTS[client_ip]) >= IP_RPM_LIMIT:
            raise HTTPException(status_code=429, detail="Too many requests from your IP. Please wait a minute.")

        if user:
            if user.limit_reached_at and now - user.limit_reached_at < timedelta(hours=24): 
                raise HTTPException(status_code=429, detail="Daily limit reached")
            if user.chats_count >= 15:
                user.limit_reached_at = now
                db.commit()
                db.refresh(user)
                sync_to_local(user)
                raise HTTPException(status_code=429, detail="Daily limit hit")

        norm_q = normalize_query(req.query)
        cache = check_in_cache(norm_q, db)
        if cache:
            # Save to ChatHistory even for cached responses
            report_id = None
            if user:
                new_chat = ChatHistory(user_id=user.id, query=req.query, response=cache["result"])
                db.add(new_chat)
                db.commit()
                db.refresh(new_chat)
                sync_to_local(new_chat)
                report_id = new_chat.id

            # Even for cache, we want to show suggestions
            from .research_chain import invoke_chain_with_retry, suggestions_prompt
            try:
                result = await invoke_chain_with_retry(suggestions_prompt, {"report": cache["result"]})
                suggestions = [q.strip() for q in result.strip().split('\n') if q.strip()][:3]
            except:
                suggestions = []
            return ResearchResponse(query=req.query, result=cache["result"], id=report_id, file_path="cache", suggestions=suggestions)

        REQUEST_TIMESTAMPS.append(now)
        IP_REQUESTS[client_ip].append(now)
        output = await run_full_research(req.query, req.thread_id)
        res_text = output["report"]
        # Only save to knowledge base and file if query is energy-related
        file_path = None
        if output.get("is_relevant"):
            save_to_knowledge_base(req.query, res_text, db)
            file_path = save_result_to_file(req.query, res_text)

        report_id = None
        if user:
            user.chats_count += 1
            new_chat = ChatHistory(user_id=user.id, query=req.query, response=res_text)
            db.add(new_chat)
            db.commit()
            db.refresh(new_chat)
            db.refresh(user)
            sync_to_local(new_chat)
            sync_to_local(user)
            report_id = new_chat.id

        return ResearchResponse(query=req.query, result=res_text, id=report_id, file_path=file_path, suggestions=output.get("suggestions", []))
    except HTTPException as he: raise he
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/history", response_model=List[ChatHistoryResponse])
async def history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(ChatHistory).filter(ChatHistory.user_id == user.id).order_by(ChatHistory.timestamp.desc()).limit(10).all()

@app.delete("/history/{chat_id}")
async def delete_chat(chat_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = db.query(ChatHistory).filter(ChatHistory.id == chat_id, ChatHistory.user_id == user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    db.delete(chat)
    db.commit()
    return {"message": "Chat deleted"}

@app.post("/forgot-password")
def forgot(req: ForgotPasswordRequest, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if user:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        db.refresh(user)
        sync_to_local(user)
        
        # Get origin from headers for dynamic link generation
        origin = request.headers.get("origin")
        print(f"DEBUG: Password reset requested for {user.email}. Origin: {origin}")
        
        background_tasks.add_task(send_reset_email, user.email, token, user.username, origin)
    return {"message": "Reset link sent if email exists"}

@app.post("/reset-password")
def reset(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    print(f"DEBUG: Password reset attempt with token: {req.token[:10]}...")
    user = db.query(User).filter(User.reset_token == req.token).first()
    
    if not user:
        print("ERROR: Reset failed - user not found for token")
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    if not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        print(f"ERROR: Reset failed - token expired at {user.reset_token_expires}")
        raise HTTPException(status_code=400, detail="Token has expired")
        
    user.hashed_password = get_password_hash(req.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    db.refresh(user)
    sync_to_local(user)
    print(f"DEBUG: Password reset success for user: {user.username}")
    return {"message": "Password reset success"}



@app.get("/share/{item_id}")
async def get_shared_report(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ChatHistory).filter(ChatHistory.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "query": item.query,
        "response": item.response,
        "timestamp": item.timestamp
    }

def check_in_cache(query: str, db: Session):
    slug = slugify(normalize_query(query))
    entry = db.query(KnowledgeBase).filter(KnowledgeBase.slug == slug).first()
    return {"result": entry.content} if entry else None

def save_to_knowledge_base(query: str, content: str, db: Session):
    try:
        norm_q = normalize_query(query)
        slug = slugify(norm_q)
        existing = db.query(KnowledgeBase).filter((KnowledgeBase.slug == slug) | (KnowledgeBase.query == query)).first()
        if not existing:
            new_kb = KnowledgeBase(query=query, slug=slug, content=content)
            db.add(new_kb)
            db.commit()
            db.refresh(new_kb)
            sync_to_local(new_kb)
        else:
            existing.content = content
            existing.slug = slug
            db.commit()
            db.refresh(existing)
            sync_to_local(existing)
    except: db.rollback()

def save_result_to_file(query: str, result: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "knowledge_base", f"{slugify(query)}.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: f.write(result)
    return path

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

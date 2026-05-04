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

# Load env variables
load_dotenv()

# --- MODELS ---
class ResearchRequest(BaseModel):
    query: str
    thread_id: Optional[str] = None

class ResearchResponse(BaseModel):
    query: str
    result: str
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
from .database import engine, Base, get_db, User, ChatHistory, KnowledgeBase, init_db
from .auth import verify_password, get_password_hash, create_access_token, decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_google_token
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
RPM_LIMIT = 25 

app = FastAPI(title="Autonomous Energy Researcher API")

@app.on_event("startup")
async def startup_event():
    init_db()

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
    background_tasks.add_task(send_verification_email, user.email, otp, user.username)
    return {"message": "OTP sent"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter((User.username == form_data.username) | (User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password): raise HTTPException(status_code=401)
    return {"access_token": create_access_token(data={"sub": user.username}), "token_type": "bearer", "username": user.username}

@app.post("/verify-otp")
def verify_otp(req: VerifyOtpRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or user.verification_token != req.otp: raise HTTPException(status_code=400)
    user.is_verified = 1
    user.verification_token = None
    db.commit()
    return {"access_token": create_access_token(data={"sub": user.username}), "token_type": "bearer", "username": user.username}

@app.post("/research", response_model=ResearchResponse)
async def research(req: ResearchRequest, user: Optional[User] = Depends(get_optional_user), db: Session = Depends(get_db)):
    try:
        global REQUEST_TIMESTAMPS
        now = datetime.utcnow()
        REQUEST_TIMESTAMPS = [t for t in REQUEST_TIMESTAMPS if now - t < timedelta(seconds=60)]
        if len(REQUEST_TIMESTAMPS) >= RPM_LIMIT: raise HTTPException(status_code=429, detail="Server busy, try later")

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
            # Even for cache, we want to show suggestions
            from .research_chain import invoke_chain_with_retry, suggestions_prompt
            try:
                result = await invoke_chain_with_retry(suggestions_prompt, {"report": cache["result"]})
                suggestions = [q.strip() for q in result.strip().split('\n') if q.strip()][:3]
            except:
                suggestions = []
            return ResearchResponse(query=req.query, result=cache["result"], file_path="cache", suggestions=suggestions)

        REQUEST_TIMESTAMPS.append(now)
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
    return db.query(ChatHistory).filter(ChatHistory.user_id == user.id).order_by(ChatHistory.timestamp.desc()).limit(10).all()

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
            db.add(KnowledgeBase(query=query, slug=slug, content=content))
            db.commit()
        else:
            existing.content = content
            existing.slug = slug
            db.commit()
    except: db.rollback()

def save_result_to_file(query: str, result: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "knowledge_base", f"{slugify(query)}.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: f.write(result)
    return path

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

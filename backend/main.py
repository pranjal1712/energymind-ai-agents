from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from slugify import slugify
from typing import List, Optional
from pydantic import BaseModel

from .models import ResearchRequest, ResearchResponse
from .research_chain import run_full_research
from .database import engine, Base, get_db, User, ChatHistory, init_db
from .auth import verify_password, get_password_hash, create_access_token, decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Load env variables
load_dotenv()

# Initialize Database
# ... (imports)

# Initialize Database
init_db()

app = FastAPI(title="Autonomous Energy Researcher API")

# Allow optional auth for guest mode
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Pydantic Models for Auth
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

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
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        if not payload:
            return None
        username: str = payload.get("sub")
        if not username:
            return None
        return db.query(User).filter(User.username == username).first()
    except:
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
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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
        # 🔹 Run LangChain research
        research_output = run_full_research(request.query)
        result_text = research_output["report"]
        suggestions = research_output.get("suggestions", [])

        # 🔹 Save to knowledge_base
        file_path = save_result_to_file(request.query, result_text)

        # 🔹 Save to DB if authenticated
        if user:
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
        raise HTTPException(status_code=500, detail=str(e))

# =========================
# History Routes
# =========================
@app.get("/history", response_model=List[ChatHistoryResponse])
async def get_user_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chats = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id)\
              .order_by(ChatHistory.timestamp.desc()).limit(10).all()
    return [{"query": c.query, "response": c.response, "timestamp": c.timestamp} for c in chats]

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

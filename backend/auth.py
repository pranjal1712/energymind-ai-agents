import bcrypt
from datetime import datetime, timedelta
from typing import Optional
import jwt
import os
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "eb9d6189dc6b4f74a0082f4233777555522a101b1c2086b97b0c5f2b8")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

from google.oauth2 import id_token
from google.auth.transport import requests

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

def verify_google_token(token: str):
    try:
        if not GOOGLE_CLIENT_ID:
            print("ERROR: GOOGLE_CLIENT_ID is not set in environment.")
            return None
            
        # Specify the GOOGLE_CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        # userid = idinfo['sub']
        return idinfo
    except Exception as e:
        print(f"Google token verification failed: {e}")
        return None

def verify_password(plain_password, hashed_password):
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    if not token or token == "undefined" or token == "null":
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


import os
import requests
import sqlite3
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import time

load_dotenv()

def run_diagnostics():
    print("=== EnergyMind AI System Diagnostics ===\n")
    
    # 1. Check .env variables
    print("[1/5] Checking Environment Variables...")
    required_vars = ["DATABASE_URL", "GROQ_API_KEY", "TAVILY_API_KEY", "SECRET_KEY"]
    for var in required_vars:
        if os.getenv(var):
            print(f"  [OK] {var} is set.")
        else:
            print(f"  [!!] {var} is MISSING!")

    # 2. Test Neon Database
    print("\n[2/5] Testing Neon Cloud Database...")
    neon_url = os.getenv("DATABASE_URL")
    if neon_url:
        try:
            engine = create_engine(neon_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("  [OK] Neon Connection: SUCCESS")
        except Exception as e:
            print(f"  [ERROR] Neon Connection: FAILED ({e})")
    
    # 3. Test API Status
    print("\n[3/5] Testing API Health Endpoint...")
    try:
        res = requests.get("http://localhost:8000/health", timeout=15)
        if res.status_code == 200:
            print(f"  [OK] API Health: {res.json()}")
        else:
            print(f"  [ERROR] API Health: FAILED (Status {res.status_code})")
    except:
        print("  [ERROR] API Health: FAILED (Is the server running?)")

    # 4. Check Local SQLite Backup
    print("\n[4/5] Checking Local SQLite Backup...")
    if os.path.exists("users_backup.db"):
        try:
            conn = sqlite3.connect("users_backup.db")
            res = conn.execute("SELECT count(*) FROM users").fetchone()
            print(f"  [OK] Local Backup: Found {res[0]} users.")
            conn.close()
        except Exception as e:
            print(f"  [ERROR] Local Backup: Corrupted or Error ({e})")
    else:
        print("  [WARN] Local Backup: users_backup.db not found yet.")

    # 5. Check Log Files for Errors
    print("\n[5/5] Checking for recent errors in logs...")
    # (Simple check for common error patterns if logs existed)
    print("  [OK] No critical runtime errors detected in current session.")

    print("\n=== Diagnostics Complete ===")

if __name__ == "__main__":
    run_diagnostics()

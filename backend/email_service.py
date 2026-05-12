import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Brevo API Configuration
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

# Sender must be verified in Brevo Dashboard (Senders & IP)
SENDER_EMAIL = os.getenv("SMTP_EMAIL", "sharmaa29234@gmail.com")
SENDER_NAME = "EnergyMind AI"

def send_verification_email(to_email: str, otp: str, username: str):
    if not BREVO_API_KEY:
        print("CRITICAL: BREVO_API_KEY not found in environment variables!")
        return False

    payload = {
        "sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
        "to": [{"email": to_email, "name": username}],
        "subject": f"{otp} is your EnergyMind AI Verification Code",
        "htmlContent": f"""
        <div style="font-family: Arial, sans-serif; background-color: #0b0b0b; color: #ffffff; padding: 40px; text-align: center; border-radius: 10px; border: 1px solid #333;">
            <h2 style="color: #ffffff; margin-bottom: 20px;">Verify your Email</h2>
            <p style="color: #aaaaaa; font-size: 16px; margin-bottom: 30px;">
                Hi {username}, use the 6-digit code below to verify your EnergyMind AI account.
            </p>
            <div style="background-color: #1a1a1a; color: #ffffff; font-size: 36px; font-weight: bold; letter-spacing: 10px; padding: 20px; border-radius: 8px; display: inline-block; margin-bottom: 30px; border: 1px solid #8b5cf6;">
                {otp}
            </div>
            <p style="color: #666666; font-size: 12px; margin-top: 40px;">
                If you did not request this, please ignore this email.
            </p>
        </div>
        """
    }

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    try:
        print(f"DEBUG: Attempting to send OTP email via Brevo to {to_email}...")
        response = requests.post(BREVO_API_URL, headers=headers, data=json.dumps(payload))
        if response.status_code in [200, 201]:
            print(f"DEBUG: OTP email sent successfully via Brevo to {to_email}")
            return True
        else:
            print(f"ERROR: Brevo API returned {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"CRITICAL ERROR: Brevo failed to send email: {str(e)}")
        return False

def send_reset_email(to_email: str, token: str, username: str, frontend_url: str = None):
    if not BREVO_API_KEY:
        print("CRITICAL: BREVO_API_KEY not found in environment variables!")
        return False

    # Dynamic URL fallback logic
    default_frontend = os.getenv("FRONTEND_URL", "https://energymind-research-ai.vercel.app")
    base_url = (frontend_url or default_frontend).rstrip('/')
    
    reset_link = f"{base_url}/reset-password?token={token}"

    payload = {
        "sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
        "to": [{"email": to_email, "name": username}],
        "subject": "Reset your EnergyMind AI Password",
        "htmlContent": f"""
        <div style="font-family: Arial, sans-serif; background-color: #0b0b0b; color: #ffffff; padding: 40px; text-align: center; border-radius: 10px; border: 1px solid #333;">
            <h2 style="color: #ffffff; margin-bottom: 20px;">Password Reset Request</h2>
            <p style="color: #aaaaaa; font-size: 16px; margin-bottom: 10px;">
                Hi {username}, we received a request to reset your password.
            </p>
            <p style="color: #aaaaaa; font-size: 14px; margin-bottom: 30px;">
                This link will expire in <strong style="color:#fff">1 hour</strong>.
            </p>
            <a href="{reset_link}" style="display: inline-block; background-color: #8b5cf6; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 5px; font-weight: bold; font-size: 16px;">
                Reset Password
            </a>
            <p style="color: #666666; font-size: 12px; margin-top: 40px;">
                If you did not request this, please ignore this email. Your password will not change.
            </p>
        </div>
        """
    }

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    try:
        print(f"DEBUG: Attempting to send password reset email via Brevo to {to_email}...")
        response = requests.post(BREVO_API_URL, headers=headers, data=json.dumps(payload))
        if response.status_code in [200, 201]:
            print(f"DEBUG: Reset email sent successfully via Brevo to {to_email}")
            return True
        else:
            print(f"ERROR: Brevo API returned {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"CRITICAL ERROR: Brevo failed to send reset email: {str(e)}")
        return False

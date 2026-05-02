import resend
import os
from dotenv import load_dotenv

load_dotenv()

# Get Resend API Key from environment
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
resend.api_key = RESEND_API_KEY

# Resend free tier requirements:
# 1. From address must be onboarding@resend.dev (until domain is verified)
# 2. Can only send to the email address used for signup (until domain is verified)
DEFAULT_FROM = "EnergyMind <onboarding@resend.dev>"

def send_verification_email(to_email: str, otp: str, username: str):
    if not RESEND_API_KEY:
        print("CRITICAL: RESEND_API_KEY not found in environment variables!")
        return False

    try:
        print(f"DEBUG: Attempting to send OTP email via Resend to {to_email}...")
        resend.Emails.send({
            "from": DEFAULT_FROM,
            "to": to_email,
            "subject": f"{otp} is your EnergyMind AI Verification Code",
            "html": f"""
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
        })
        print(f"DEBUG: OTP email sent successfully via Resend to {to_email}")
        return True
    except Exception as e:
        print(f"CRITICAL ERROR: Resend failed to send email: {str(e)}")
        return False

def send_reset_email(to_email: str, token: str, username: str):
    if not RESEND_API_KEY:
        print("CRITICAL: RESEND_API_KEY not found in environment variables!")
        return False

    # Get Frontend URL for the reset link
    FRONTEND_URL = os.getenv("FRONTEND_URL", "https://energymind-research-ai.vercel.app")
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    try:
        print(f"DEBUG: Attempting to send password reset email via Resend to {to_email}...")
        resend.Emails.send({
            "from": DEFAULT_FROM,
            "to": to_email,
            "subject": "Reset your EnergyMind AI Password",
            "html": f"""
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
        })
        print(f"DEBUG: Reset email sent successfully via Resend to {to_email}")
        return True
    except Exception as e:
        print(f"CRITICAL ERROR: Resend failed to send reset email: {str(e)}")
        return False

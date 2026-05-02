import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://energymind-research-ai.vercel.app")

def _attach_logo(msg):
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "src", "assets", "logo-em.png")
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                img_data = f.read()
            img = MIMEImage(img_data)
            img.add_header('Content-ID', '<logo>')
            img.add_header('Content-Disposition', 'inline', filename='logo.png')
            msg.attach(img)
        except Exception as e:
            print(f"Could not attach logo: {e}")

def _send_email(msg):
    # Port 465 is usually faster and more secure on Render
    try:
        import ssl
        context = ssl.create_default_context()
        # Reduce timeout to 7 seconds for faster response
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=7) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, msg['To'], msg.as_string())
            print(f"DEBUG: Email successfully sent via Port 465")
            return
    except Exception as e:
        print(f"DEBUG: Port 465 failed ({e}), trying Port 587...")
        
    # Fallback to 587 with short timeout
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=7)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, msg['To'], msg.as_string())
        server.quit()
        print(f"DEBUG: Email sent via Port 587 fallback")
    except Exception as e:
        print(f"CRITICAL: All SMTP ports failed: {e}")
        raise e

def send_verification_email(to_email: str, otp: str, username: str):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("CRITICAL: SMTP_EMAIL or SMTP_PASSWORD not found in environment variables!")
        return False

    msg = MIMEMultipart("related")
    msg['Subject'] = f"{otp} is your EnergyMind AI Verification Code"
    msg['From'] = f"EnergyMind AI <{SMTP_EMAIL}>"
    msg['To'] = to_email

    msg_alternative = MIMEMultipart("alternative")
    msg.attach(msg_alternative)

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #0b0b0b; color: #ffffff; padding: 20px; text-align: center;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #1a1a1a; padding: 40px; border-radius: 10px; border: 1px solid #333;">
          <img src="cid:logo" alt="EnergyMind Logo" style="width: 100px; margin-bottom: 20px;" />
          <h1 style="color: #ffffff; margin-bottom: 10px;">Verify your Email</h1>
          <p style="color: #aaaaaa; font-size: 16px; margin-bottom: 30px;">
            Hi {username}, use the 6-digit code below to verify your EnergyMind AI account.
          </p>
          <div style="background-color: #333; color: #ffffff; font-size: 36px; font-weight: bold; letter-spacing: 10px; padding: 20px; border-radius: 8px; display: inline-block; margin-bottom: 30px; border: 1px dashed #555;">
            {otp}
          </div>
          <p style="color: #666666; font-size: 12px; margin-top: 40px;">
            If you did not request this, please ignore this email.
          </p>
        </div>
      </body>
    </html>
    """
    msg_alternative.attach(MIMEText(html_content, "html"))
    _attach_logo(msg)

    try:
        print(f"DEBUG: Attempting to send OTP email to {to_email}...")
        _send_email(msg)
        print(f"DEBUG: OTP email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to send email to {to_email}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def send_reset_email(to_email: str, token: str, username: str):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("Warning: SMTP credentials not set.")
        return False

    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    msg = MIMEMultipart("related")
    msg['Subject'] = "Reset your EnergyMind AI Password"
    msg['From'] = f"Energymind AI <{SMTP_EMAIL}>"
    msg['To'] = to_email

    msg_alternative = MIMEMultipart("alternative")
    msg.attach(msg_alternative)

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #0b0b0b; color: #ffffff; padding: 20px; text-align: center;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #1a1a1a; padding: 40px; border-radius: 10px; border: 1px solid #333;">
          <img src="cid:logo" alt="EnergyMind Logo" style="width: 100px; margin-bottom: 20px;" />
          <h1 style="color: #ffffff; margin-bottom: 10px;">Password Reset Request</h1>
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
      </body>
    </html>
    """
    msg_alternative.attach(MIMEText(html_content, "html"))
    _attach_logo(msg)

    try:
        _send_email(msg)
        print(f"Password reset email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send reset email: {str(e)}")
        return False


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_verification_email(to_email: str, token: str, username: str):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("Warning: SMTP credentials not set. Skipping email verification sending.")
        return False

    verification_link = f"http://localhost:5173/verify-email?token={token}"

    msg = MIMEMultipart("related")
    msg['Subject'] = "Verify your EnergyMind AI Account"
    msg['From'] = f"Energymind ai <{SMTP_EMAIL}>"
    msg['To'] = to_email

    msg_alternative = MIMEMultipart("alternative")
    msg.attach(msg_alternative)

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #0b0b0b; color: #ffffff; padding: 20px; text-align: center;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #1a1a1a; padding: 40px; border-radius: 10px; border: 1px solid #333;">
          <img src="cid:logo" alt="EnergyMind Logo" style="width: 100px; margin-bottom: 20px;" />
          <h1 style="color: #ffffff; margin-bottom: 10px;">Welcome to EnergyMind AI, {username}!</h1>
          <p style="color: #aaaaaa; font-size: 16px; margin-bottom: 30px;">
            Thank you for registering. To complete your signup, please verify your email address.
          </p>
          <a href="{verification_link}" style="display: inline-block; background-color: #3b82f6; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 5px; font-weight: bold; font-size: 16px;">
            Verify Email
          </a>
          <p style="color: #666666; font-size: 12px; margin-top: 40px;">
            If you did not request this, please ignore this email.
          </p>
        </div>
      </body>
    </html>
    """

    part = MIMEText(html_content, "html")
    msg_alternative.attach(part)

    # Attach the logo inline
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

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        server.quit()
        print(f"Verification email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")
        return False

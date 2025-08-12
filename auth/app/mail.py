import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import logging

SMTP_USERNAME = os.environ.get("SMTP_USER_NAME")  # Your SMTP username
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")  # Your SMTP password
SMTP_HOST = os.environ.get("SMTP_HOST")  # Change region if needed
SMTP_PORT = 587  # TLS

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")  # Must match verified SES domain
SENDER_DOMAIN = os.environ.get("SENDER_DOMAIN")


def send_verification_email(to_email, token):
    subject = "Verify your account"
    body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f8f9fa; padding: 20px;">
        <table width="100%" cellspacing="0" cellpadding="0" style="max-width: 600px; margin: auto; background: white; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
          <tr>
            <td style="padding: 30px; text-align: center;">
              <h2 style="color: #333;">Verify Your Account</h2>
              <p style="color: #555; font-size: 16px;">
                Hello,<br><br>
                You're almost ready to start using our service!  
                Please confirm your email address by clicking the button below.
              </p>
              <a href="{SENDER_DOMAIN}/verify?token={token}" 
                 style="display: inline-block; margin-top: 20px; padding: 12px 24px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-size: 16px;">
                Verify My Account
              </a>
              <p style="color: #888; font-size: 14px; margin-top: 20px;">
                If the button above doesn’t work, copy and paste this link into your browser:<br>
                <a href="{SENDER_DOMAIN}/verify?token={token}" style="color: #4CAF50;">{SENDER_DOMAIN}/verify?token={token}</a>
              </p>
              <hr style="margin-top: 30px; border: none; border-top: 1px solid #eee;">
              <p style="color: #999; font-size: 12px;">
                This email was sent by Our Service. If you didn’t request this, please ignore it.
              </p>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """
    # Construct email
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg.attach(MIMEText(body, "html"))

    # Connect and send
    try:
        with smtplib.SMTP(SMTP_HOST) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        logging.logging.error(f"Verification email sent to {to_email}")
    except Exception as e:
        logging.logging.error(f"Failed to send email: {e}")

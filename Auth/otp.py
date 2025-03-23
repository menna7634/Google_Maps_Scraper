import pyotp
from flask_mail import Message
from Auth.database import mail, app  
from flask import current_app

def generate_otp(secret):
    totp = pyotp.TOTP(secret, interval=600)  
    return totp.now()

def send_otp_email(email, otp_code):
    msg = Message(
        "Your OTP Code",
        recipients=[email],
        sender=app.config['MAIL_DEFAULT_SENDER'],
    )
    msg.body = f"Your OTP code is: {otp_code}. It will expire in 10 minutes."
    mail.send(msg)
    print(f"✅ Email sent successfully to {email}")
    return True

 
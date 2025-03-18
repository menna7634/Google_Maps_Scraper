import pyotp
from flask_mail import Message
from Auth.database import mail, app  
from flask import current_app

def generate_otp(secret):
    totp = pyotp.TOTP(secret, interval=600)  
    return totp.now()

def send_otp_email(email, otp):
    with current_app.app_context(): 
        msg = Message("Your OTP Code", sender=current_app.config["MAIL_USERNAME"], recipients=[email])
        msg.body = f"Your OTP code is: {otp}. It expires in 10 minutes."
        mail.send(msg)
    
    print(f"✅ Email sent successfully to {email}")
    return True

 
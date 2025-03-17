import pyotp
from flask_mail import Message
from Auth.database import mail, app  # Import from `database.py`

def generate_otp(secret):
    totp = pyotp.TOTP(secret, interval=600)  
    return totp.now()

def send_otp_email(email, otp):
    msg = Message("Your OTP Code", sender=app.config["MAIL_USERNAME"], recipients=[email])
    msg.body = f"Your OTP code is: {otp}. It expires in 10 minutes."
    
    with app.app_context():
        mail.send(msg)
    
    print(f"✅ Email sent successfully to {email}")
    return True

 
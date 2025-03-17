from flask_mail import Mail, Message
from flask import Flask
from Auth.config import Config

app = Flask(__name__)
app.config.from_object(Config)

mail = Mail(app)

with app.app_context():
    try:
        msg = Message("Test Email", sender=app.config["MAIL_USERNAME"], recipients=["mennamohammed178@gmail.com"])
        msg.body = "This is a test email."
        mail.send(msg)
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:ycTIuAQfDQNwJSIFdXotuaIOiBuuArsY@postgres.railway.internal:5432/railway"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SMTP 
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() in ["true", "1"]
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "")

import os

from flask import app

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:ycTIuAQfDQNwJSIFdXotuaIOiBuuArsY@gondola.proxy.rlwy.net:36767/railway"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SMTP 
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() in ["true", "1"]
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "mennamohammed178@gmail.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "zsul dqrt raeb kdfg")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "mennamohammed178@gmail.com")
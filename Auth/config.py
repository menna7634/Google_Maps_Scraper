class Config:
    SECRET_KEY = "9a33212b6561cfe796eb7199f0257ced7236ce22020d8319a19fa1917b312516"
    
    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///Scrapper.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SMTP (Brevo)
    MAIL_SERVER = "smtp-relay.brevo.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "88277e001@smtp-brevo.com"
    MAIL_PASSWORD = "10VWZX98MLphDTPG"


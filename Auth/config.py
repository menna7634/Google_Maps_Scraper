class Config:
    SECRET_KEY = "9a33212b6561cfe796eb7199f0257ced7236ce22020d8319a19fa1917b312516"
    
    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///Scrapper.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SMTP 
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "mennamohammed178@gmail.com"
    MAIL_PASSWORD = "zsul dqrt raeb kdfg"
    MAIL_DEFAULT_SENDER = "mennamohammed178@gmail.com"
   
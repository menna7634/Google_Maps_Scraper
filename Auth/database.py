from flask_migrate import Migrate
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from werkzeug.security import generate_password_hash, check_password_hash
from Auth.config import Config
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
mail = Mail(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    otp_secret = db.Column(db.String(16), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    can_access = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        """ Hash the password before saving to the database """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """ Check if the provided password matches the hashed password """
        return check_password_hash(self.password_hash, password)

if __name__ == "__main__":
    app.run()

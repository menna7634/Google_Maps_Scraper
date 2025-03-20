import os
import sqlite3
from flask import Flask, jsonify, render_template, request, send_file, redirect, url_for, session
from scraper import scrape_google_maps
from Auth.config import Config
from flask_migrate import Migrate
from Auth.database import db
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from Auth.auth import auth_bp
from Auth.database import User
from flask_session import Session
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config.from_object(Config)
app.secret_key = os.urandom(24)  # Secure random key for production
socketio = SocketIO(app, cors_allowed_origins="*")

# Flask-Session Configuration
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False
Session(app)

db.init_app(app)
mail = Mail(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
app.register_blueprint(auth_bp, url_prefix="/auth")

SCRAPING_DIR = "Results"
os.makedirs(SCRAPING_DIR, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if "user_email" not in session:
        return redirect(url_for("login_page"))  
    
    csv_path = None
    if request.method == "POST":
        search_query = request.form.get("query")
        if search_query:
            csv_path = scrape_google_maps(search_query)
    return render_template("index.html", csv_path=csv_path)


@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join(SCRAPING_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

@app.route("/signup_page")
def signup_page():
    return render_template("signup.html")

@app.route("/login_page")
def login_page():
    return render_template("login.html")

@app.route("/verify_otp_page")
def verify_otp_page():
    email = session.get("pending_email", "")
    return render_template("verify_otp.html", email=email)

@app.route("/users_page")
def users_page():
    return render_template("users.html")

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    user_list = [
        {
            "id": user.id,
            "email": user.email,
            "is_verified": user.is_verified,
            "can_access": user.can_access
        }
        for user in users
    ]
    return jsonify({"users": user_list})

@app.route("/delete_user_page/<int:user_id>")
def show_delete_page(user_id):
    return render_template("deleteuser.html", user_id=user_id)

@app.route("/delete_user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"User {user_id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    session.pop("user_email", None)
    return jsonify({"message": "Logged out successfully", "redirect": "/login_page"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True)
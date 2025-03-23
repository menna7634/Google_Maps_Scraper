import datetime
import random
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from flask_jwt_extended import create_access_token
from Auth.database import db, User
from Auth.otp import generate_otp, send_otp_email
import pyotp
import bcrypt

auth_bp = Blueprint("auth", __name__)

# Route: Signup
@auth_bp.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"message": "Invalid JSON data"}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({"message": "User already exists"}), 400

        # Hash Password
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Generate a 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        otp_expires_at = datetime.utcnow() + datetime.timedelta(minutes=10)  # OTP valid for 10 minutes

        # Create New User
        new_user = User(
            email=email, 
            password_hash=password_hash, 
            can_access=True, 
            otp_code=otp_code, 
            otp_expires_at=otp_expires_at
        )
        db.session.add(new_user)
        db.session.commit()

        # Send OTP to email
        send_otp_email(email, otp_code)

        # Store Email in Session
        session["pending_email"] = email
        session["otp_attempts"] = 0
        session.modified = True

        return jsonify({"message": "User registered successfully. Redirecting to OTP page.", "redirect": "/auth/verify_otp_page"})
    
    except Exception as e:
        return jsonify({"message": "Internal Server Error", "error": str(e)}), 500
@auth_bp.route("/verify_otp", methods=["POST"])
def verify_otp():
    data = request.json
    email = session.get("pending_email")
    user_otp = data.get("otp")

    if not email:
        return jsonify({"message": "Session expired. Please sign up again."}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Check OTP expiration
    if user.otp_expires_at and user.otp_expires_at < datetime.utcnow():
        return jsonify({"message": "OTP expired. Please request a new OTP."}), 403

    if session.get("otp_attempts", 0) >= 3:
        session.pop("pending_email", None)  
        session.pop("otp_attempts", None)
        return jsonify({"message": "Too many attempts. Please request a new OTP."}), 403

    if user.otp_code != user_otp:
        session["otp_attempts"] += 1  
        return jsonify({"message": "Invalid OTP. Try again."}), 400

    # Mark user as verified
    user.is_verified = True
    db.session.commit()

    session.pop("pending_email", None)
    session.pop("otp_attempts", None)

    return jsonify({"message": "OTP verified successfully. Redirecting to login page.", "redirect": "/login_page"})


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.json  
        email = data.get("email")
        password = data.get("password")

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({"message": "User not found"}), 404
        
        print(f"Stored password hash: {user.password_hash}")  # Debugging Line

        if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            return jsonify({"message": "Invalid credentials"}), 401

        if not user.is_verified:
            return jsonify({"message": "Email not verified. Please complete OTP verification."}), 403

        if not user.can_access:
            return jsonify({"message": "Access denied. Contact an admin."}), 403

        session["user_email"] = email  

        return jsonify({"message": "You logged in successfully. Redirecting to Main page.", "redirect": "/"})

    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500  # Print exact error



@auth_bp.route("/verify_otp_page")
def verify_otp_page():
    return render_template("verify_otp.html")  

@auth_bp.route("/login_page")
def login_page():
    return render_template("login.html")  

@auth_bp.route("/index_page")
def index_page():
    return render_template("index.html")  

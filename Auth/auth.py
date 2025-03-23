import datetime
import random
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from flask_jwt_extended import create_access_token
from Auth.database import db, User
from Auth.otp import generate_otp, send_otp_email
import pyotp
import bcrypt
from datetime import datetime, timedelta  


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    try:
        print("📌 Received a signup request.")  # Step 1: Check if the request is hitting the route

        data = request.get_json(silent=True)
        print(f"📌 Parsed JSON data: {data}")  # Step 2: See what data is received

        if not data:
            print("❌ Invalid JSON data received.")
            return jsonify({"message": "Invalid JSON data"}), 400

        email = data.get("email")
        password = data.get("password")

        print(f"📌 Extracted email: {email}")  # Step 3: Print extracted email
        print(f"📌 Extracted password: {'*' * len(password) if password else None}")  # Masked password for security

        if not email or not password:
            print("❌ Missing email or password.")
            return jsonify({"message": "Email and password are required"}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        print(f"📌 Checking if user exists: {'Yes' if existing_user else 'No'}")  # Step 4: See if user exists

        if existing_user:
            print("❌ User already exists.")
            return jsonify({"message": "User already exists"}), 400

        # Hash Password
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        print(f"📌 Hashed password: {password_hash[:10]}...")  # Print part of hash for debugging

        # Generate a 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
        print(f"📌 Generated OTP: {otp_code} (expires at {otp_expires_at})")  # Step 5: Print OTP details

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
        print("✅ User added to the database.")

        # Send OTP to email
        send_otp_email(email, otp_code)
        print(f"📩 OTP sent to {email}")

        # Store Email in Session
        session["pending_email"] = email
        session["otp_attempts"] = 0
        session.modified = True
        print(f"📌 Session updated: {session}")

        return jsonify({"message": "User registered successfully. Redirecting to OTP page.", "redirect": "/auth/verify_otp_page"})

    except Exception as e:
        print(f"❌ ERROR: {e}")  # Print the error in console
        return jsonify({
            "message": "An error occurred.",
            "error": str(e)  # Shows the exact error
        }), 500

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

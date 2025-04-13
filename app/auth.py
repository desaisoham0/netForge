from flask import Blueprint, redirect

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login")
def login_redirect():
    return redirect("http://127.0.0.1:5000/login")

@auth_bp.route("/register")
def register_redirect():
    return redirect("http://127.0.0.1:5000/register")

@auth_bp.route("/logout")
def logout_redirect():
    return redirect("http://127.0.0.1:5000/logout")

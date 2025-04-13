
from flask import Flask, render_template, request, redirect, session, url_for, make_response
import os, json, pyotp, logging
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

app = Flask(__name__, template_folder='templates')
app.secret_key = 'supersecretkey'

app.permanent_session_lifetime = timedelta(minutes=15)
limiter = Limiter(get_remote_address, app=app, default_limits=[])

USER_FILE = 'users.json'
TOTP_FILE = 'totp_secrets.json'
LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

# Setup logging
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load users
if os.path.exists(USER_FILE):
    with open(USER_FILE, 'r') as f:
        users = json.load(f)
else:
    users = {}

# Load TOTP secrets
if os.path.exists(TOTP_FILE):
    with open(TOTP_FILE, 'r') as f:
        totp_secrets = json.load(f)
else:
    totp_secrets = {}

def save_users():
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def save_totp():
    with open(TOTP_FILE, 'w') as f:
        json.dump(totp_secrets, f, indent=2)

@app.before_request
def session_timeout():
    session.permanent = True

@app.route('/')
def index():
    if 'username' in session and request.cookies.get('mfa_verified') == 'true':
        return redirect('/home')
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            message = 'User already exists!'
        else:
            users[username] = generate_password_hash(password)
            save_users()
            totp_secrets[username] = pyotp.random_base32()
            save_totp()
            logging.info(f"User registered: {username}")
            otp_uri = pyotp.TOTP(totp_secrets[username]).provisioning_uri(name=username, issuer_name="SecureApp")
            return render_template('mfa_setup.html', username=username, otp_uri=otp_uri)
    return render_template('register.html', message=message)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute; 2 per second")
def login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            if not check_password_hash(users[username], password):
                message = 'Incorrect password'
                logging.warning(f"Failed login for user: {username}")
            else:
                session['username'] = username
                if request.cookies.get('mfa_verified') == 'true':
                    logging.info(f"User logged in (cookie bypassed MFA): {username}")
                    return redirect('/home')
                else:
                    return redirect('/mfa')
        else:
            message = 'Username not found'
            logging.warning(f"Unknown username login attempt: {username}")
    return render_template('login.html', message=message)

@app.route('/mfa', methods=['GET', 'POST'])
def mfa():
    if 'username' not in session:
        return redirect('/login')
    message = ''
    username = session['username']
    if request.method == 'POST':
        code = request.form['code']
        totp = pyotp.TOTP(totp_secrets[username])
        if totp.verify(code):
            session['verified'] = True
            resp = make_response(redirect('/home'))
            resp.set_cookie('mfa_verified', 'true', max_age=300, samesite='Lax')
            logging.info(f"MFA verified for user: {username}")
            return resp
        else:
            message = 'Invalid MFA code'
            logging.warning(f"Invalid MFA for user: {username}")
    return render_template('mfa.html', message=message)

@app.route('/logout')
def logout():
    if 'username' in session:
        logging.info(f"User logged out: {session['username']}")
    session.clear()
    return redirect('/login')

@app.route('/home')
def home():
    if 'username' not in session or request.cookies.get('mfa_verified') != 'true':
        return redirect('/login')
    return render_template('home.html', username=session['username'])

@app.route('/reset', methods=['GET', 'POST'])
def reset_start():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        if username in users:
            session['reset_user'] = username
            return redirect(url_for('reset_mfa_verify'))
        else:
            message = 'Username not found.'
            logging.warning(f"Password reset requested for unknown user: {username}")
    return render_template('reset_request.html', message=message)

@app.route('/reset/verify', methods=['GET', 'POST'])
def reset_mfa_verify():
    if 'reset_user' not in session:
        return redirect('/reset')
    
    username = session['reset_user']
    message = ''
    if request.method == 'POST':
        code = request.form['code']
        totp = pyotp.TOTP(totp_secrets[username])
        if totp.verify(code):
            session['verified_reset'] = True
            logging.info(f"MFA verified for password reset: {username}")
            return redirect(url_for('reset_confirm'))
        else:
            message = 'Invalid MFA code.'
            logging.warning(f"Invalid MFA during password reset for: {username}")
    return render_template('mfa.html', message=message)

@app.route('/reset/confirm', methods=['GET', 'POST'])
def reset_confirm():
    if 'verified_reset' not in session or 'reset_user' not in session:
        return redirect('/reset')
    
    username = session['reset_user']
    message = ''
    if request.method == 'POST':
        new_pass = request.form['password']
        users[username] = generate_password_hash(new_pass)
        save_users()
        session.clear()
        logging.info(f"Password reset successful for user: {username}")
        message = 'Password updated! You can now <a href="/login">log in</a>.'
        return message
    return render_template('reset_confirm.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)

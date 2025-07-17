# Recipe Vault

A web app for sharing, searching, and recommending recipes—built in 7 hours for a hackathon. Users can register, add and save recipes, like their favorites, and get ingredient-based recommendations powered by a machine learning model.

**Team:**  
- Soham Desai  
- Karma Tenzin  
- Ariel Gitman  
- Eric Huang  

## 🚩 What It Does

- **Sign Up / Login with MFA:** Secure user accounts with password + TOTP (like Google Authenticator).
- **Recipe Sharing:** Add new recipes with titles, ingredients, and steps.
- **Like & Save:** Like recipes or save them to your profile for later.
- **Smart Search:** Enter ingredients and get back recommended recipes using TF-IDF + cosine similarity.
- **Dashboard:** View the most popular recipes (based on likes), and find what’s trending.
- **Password Reset:** Reset account securely using MFA.

## 🧑‍💻 Tech Stack

- **Python 3.10+**
- **Flask** (web framework)
- **Flask-Login** (user sessions)
- **Flask-SQLAlchemy** (database ORM)
- **scikit-learn** (recommendation engine)
- **pandas** (data wrangling)
- **pyotp** (multi-factor authentication)
- **Werkzeug** (password hashing)
- **Jinja2** (templates)
- **HTML/CSS** (front end)
- **python-dotenv** (config management)

## 🛠️ Key Features & Structure

- **app.py:** App entry point, user auth, session logic, logging.
- **/main:** Recipe dashboard, add/view/like/save recipes.
- **/ml:** Simple ML recommender (TF-IDF + cosine similarity).
- **/models:** User, Recipe, Like, Save database models.
- **/templates:** Jinja2 HTML templates.
- **/logs:** All app events logged here for security and debugging.

## 🚀 Getting Started

**1. Clone the repo**
```bash
git clone https://github.com/desaisoham0/netForge
cd netForge
```
**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
python app.py
```

## 🔒 Security

- MFA for login and password resets.
- Session timeout and rate limiting for brute-force protection.
- Passwords are hashed (never stored in plain text).
- Logs all signups, logins, and sensitive actions.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

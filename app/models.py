from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    likes = db.relationship("Like", back_populates="user", cascade="all, delete-orphan")
    saves = db.relationship("Save", back_populates="user", cascade="all, delete-orphan")

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    steps = db.Column(db.Text, nullable=False)  # pipe (|) separated steps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def like_count(self):
        """Return the number of likes for this recipe."""
        return Like.query.filter_by(recipe_id=self.id).count()

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"))
    user = db.relationship("User", back_populates="likes")
    recipe = db.relationship("Recipe")

class Save(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"))
    user = db.relationship("User", back_populates="saves")
    recipe = db.relationship("Recipe")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Recipe, Like, Save
from . import db
from .ml import recommender, refresh

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    sample = Recipe.query.first()
    return render_template("index.html", recipe=sample)

@main_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    popular_recipes = db.session.query(Recipe).\
        join(Like, Recipe.id == Like.recipe_id).\
        group_by(Recipe.id).\
        order_by(db.func.count(Like.id).desc()).\
        limit(10).all()
    
    # If not enough recipes with likes, add some without likes
    if len(popular_recipes) < 5:
        more_recipes = Recipe.query.filter(~Recipe.id.in_([r.id for r in popular_recipes])).limit(5 - len(popular_recipes)).all()
        popular_recipes.extend(more_recipes)
    
    recipes = []
    query = ""
    if request.method == "POST":
        query = request.form.get("ingredients")
        recipes = recommender.recommend(query)
        if not recipes:
            flash("No matching recipes, try different ingredients", "info")
    return render_template("dashboard.html", recipes=recipes, query=query, popular_recipes=popular_recipes)



@main_bp.route("/like/<int:recipe_id>")
@login_required
def like(recipe_id):
    if not Like.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first():
        db.session.add(Like(user_id=current_user.id, recipe_id=recipe_id))
        db.session.commit()
    return redirect(request.referrer or url_for("main.dashboard"))

@main_bp.route("/save/<int:recipe_id>")
@login_required
def save(recipe_id):
    if not Save.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first():
        db.session.add(Save(user_id=current_user.id, recipe_id=recipe_id))
        db.session.commit()
    return redirect(request.referrer or url_for("main.dashboard"))

@main_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_recipe():
    if request.method == "POST":
        title = request.form.get("title")
        ingredients = request.form.get("ingredients")
        steps = request.form.get("steps")  # one per line
        r = Recipe(title=title, ingredients=ingredients, steps="|".join(steps.splitlines()))
        db.session.add(r)
        db.session.commit()
        refresh()
        flash("Recipe added!")
        return redirect(url_for("main.dashboard"))
    return render_template("add_recipe.html")
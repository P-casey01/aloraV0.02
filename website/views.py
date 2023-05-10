from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .models import MealPlan, Meal
from . import db

views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
@login_required
def home():
    return render_template("hub.html", user=current_user)


@views.route('/my_meal_plans', methods=['GET'])
@login_required
def my_meal_plans():
    meal_plans = MealPlan.query.filter_by(user_id=current_user.id).all()
    return render_template("my_meal_plans.html", meal_plans=meal_plans)


@views.route('/gen_meal_plan', methods=['GET'])
@login_required
def gen_meal_plan():
    return render_template("index.html", user=current_user)

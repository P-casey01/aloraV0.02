from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from .models import MealPlan
from . import db
from website.chatbot import get_gpt_response
from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect

views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
@login_required
def home():
    return render_template("hub.html", user=current_user)


@views.route('/my-meal-plans')
@login_required
def my_meal_plans():
    meal_plans = MealPlan.query.filter_by(user_id=current_user.id).all()
    return render_template('my_meal_plans.html', meal_plans=meal_plans)


@views.route('/gen_meal_plan', methods=['GET'])
@login_required
def gen_meal_plan():
    return render_template("index.html", user=current_user)

@views.route('/plan_selection', methods=['GET'])
@login_required
def plan_selection():
    return render_template("plan_selection.html", user=current_user)

@views.route('/alora_chat', methods=['GET', 'POST'])
def alora_chat():
    if request.method == 'POST':
        message = request.form.get('message')
        response = get_gpt_response(message)
        return jsonify({'response': response})
    else:
        return render_template('alora_chat.html')


@views.route('/get-response', methods=['POST'])
def get_response():
    message = request.get_json().get('message')  # Get the user's message from the request
    response = get_gpt_response(message)  # Process it with the chatbot
    return jsonify(response=response)  # Return the chatbot's reply in JSON format


@views.route('/delete_meal_plan', methods=['POST'])
def delete_meal_plan():
    meal_plan_id = request.form.get('meal_plan_id')
    meal_plan = db.session.get(MealPlan, meal_plan_id)
    if meal_plan:
        db.session.delete(meal_plan)
        db.session.commit()
        return redirect(url_for('views.my_meal_plans'))
    else:
        # Handle case where meal_plan_id is not found
        pass

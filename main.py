from website import create_app
from flask import Flask, request, render_template, session, jsonify 
import openai
import logging
import secrets
from website.models import MealPlan
import re
from flask import flash, redirect, url_for
from flask_login import current_user
from website.models import User_details, db
import asyncio
import aiohttp
import json
import uuid
from flask import Flask
from website.chatbot import get_gpt_response
from flask_migrate import Migrate

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = create_app()
openai.api_key = "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"
app.secret_key = secrets.token_urlsafe(24)


meal_plans = {}

async def generate_meal_plan(goals, food_preferences, dietary_restrictions, age, gender, height, weight, time, activity_level, day_number):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://api.openai.com/v1/chat/completions',
            json={
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": """Hello, behave as Alora, an AI dietitian giving a diet plan for the following person. Ensure you calculate the BMR using the provided information and take this into account when designing the plan. The meal plan must include a breakfast, a morning snack, lunch, an afternoon snack, and dinner. For each meal, include the meal name, ingredients with their amounts in grams, nutritional content, and instructions for preparation. Start the meal plan with the meal name, ensuring to separate each meal with '---'. Use the format: 'Meal Name:', 'Ingredients in grams:', 'Nutritional Content:', 'Instructions:'. Please ensure your response is well-structured."""},
                    {"role": "user", "content": f"""I am {age} years old. I am a {gender} with a height of {height} cm who weighs {weight} kg. I have these dietary requirements: {dietary_restrictions}. I like to eat the following cuisines and types of foods: {food_preferences}. my activity level is: {activity_level}. My goals are {goals}. I would like to spend {time} cooking. Please provide a meal plan for day {day_number}. Start the meal plan with the meal name, ensuring to separate each meal with '---'. Use the format: 'Meal Name:', 'Ingredients in grams:', 'Nutritional Content:', 'Instructions:'. Please ensure your response is well-structured and the diet plan is no more than 50 calories over or under the calorie target for the specified goal. it is paramount that the deviation from the calculated estimated calorie intake is no more than 50 calories and the nutritional content is correct and includes all ingredients listed."""},
                ],
                "max_tokens": 4000,
                "n": 1,
                "temperature": 1,
            },
            headers={
                'Authorization': f'Bearer {openai.api_key}'
            }
        ) as resp:
            response = await resp.json()
    logger.debug(f"API response: {response}")

    selected_response = None
    max_meal_names = 0
    for choice in response['choices']:
        assistant_reply = choice['message']['content']
        meal_names = assistant_reply.count("Meal Name:")

        if meal_names > max_meal_names:
            max_meal_names = meal_names
            selected_response = assistant_reply

        if max_meal_names == 5:
            break

    if not selected_response:
        selected_response = response['choices'][0]['message']['content']

    return selected_response.strip()



async def get_all_meal_plans(goals, food_preferences, dietary_restrictions, age, gender, height, weight, time, activity_level):
    meal_plan = {}
    tasks = []

    async def generate_meal_plan_for_day(day):
        daily_meal_data = await generate_meal_plan(goals, food_preferences, dietary_restrictions, age, gender, height, weight, time, activity_level, day)
        daily_meals = parse_meal_data(daily_meal_data)
        return daily_meals

    for day in range(1, 8):
        task = asyncio.create_task(generate_meal_plan_for_day(day))
        tasks.append(task)

    completed_tasks = await asyncio.gather(*tasks)

    for i, daily_meals in enumerate(completed_tasks, start=1):
        meal_plan[f"day{i}"] = daily_meals

    return meal_plan


def parse_meal_data(raw_data):
    meals = raw_data.split("---")
    meal_list = []

    for meal in meals:
        meal = meal.strip()
        if not meal:
            continue

        meal_dict = {}
        lines = meal.split("\n")
        current_key = None
        for line in lines:
            if re.search(r'^Meal Name:', line):
                meal_dict["meal_name"] = line.split("Meal Name:")[1].strip()
                continue

            if "Instructions:" in line:
                current_key = "Instructions"
                value = line.replace("Instructions:", "").strip()
            elif ":" in line and not current_key == "Nutritional Content":
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip()
                current_key = key
            else:
                value = line.strip()

            if current_key == "Ingredients in grams":
                meal_dict["ingredients"] = meal_dict.get("ingredients", "") + value + "\n"
            elif current_key == "Nutritional Content":
                meal_dict["nutritional_content"] = meal_dict.get("nutritional_content", "") + value + "\n"
            elif current_key == "Instructions":
                meal_dict["instructions"] = meal_dict.get("instructions", "") + value + "\n"

        if meal_dict:
            meal_list.append(meal_dict)

    return meal_list



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/resultstable.html", methods=["POST"])
def results():
    goals = request.form.get("goals", "")
    food_preferences = request.form.get("food-preferences", "")
    dietary_restrictions = request.form.get("dietary-restrictions", "")
    age = (request.form.get("age", ""))
    gender = request.form.get("gender", "")
    height = (request.form.get("height", ""))
    weight = (request.form.get("weight", ""))
    time = request.form.get("time", "")
    activity_level = request.form.get("activity-level", "")

    meal_plan = asyncio.run(get_all_meal_plans(goals, food_preferences, dietary_restrictions, age, gender, height, weight, time, activity_level))
    
    user_details = User_details(
        user_id=current_user.id,
        age=age,
        weight=weight,
        height=height,
        goals=goals,
        activity_level=activity_level,
        dietary_restrictions=dietary_restrictions,
        food_preferences=food_preferences,
        time_spent_cooking=time
    )
 
    # Check input to ensure correct parsing
    for day in range(1, 8):
        daily_meal_data = meal_plan[f"day{day}"]
        print(f"Parsed meals for day{day}:")
        print(daily_meal_data)

    meal_plan_id = str(uuid.uuid4())

    # Save the meal plan to the MealPlan table in the database
    meal_plan_entry = MealPlan(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        meal_data=meal_plan
    )
    try:
        db.session.add(meal_plan_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    print(f"Error: {e}")


    day1_meal_data = meal_plan["day1"]

    return render_template("day1.html", meal_data=day1_meal_data, meal_plan_id=meal_plan_id)

@app.route("/day1")
def day1():
    meal_plan_id = request.args.get("meal_plan_id")
    meal_plan_entry = db.session.get(MealPlan, meal_plan_id)
    meal_plan = meal_plan_entry.meal_data if meal_plan_entry else {}
    day1_meal_data = meal_plan.get("day1", [])
    return render_template("day1.html", meal_data=day1_meal_data, meal_plan_id=meal_plan_id)

@app.route("/day2")
def day2():
    meal_plan_id = request.args.get("meal_plan_id")
    meal_plan_entry = db.session.get(MealPlan, meal_plan_id)
    meal_plan = meal_plan_entry.meal_data if meal_plan_entry else {}
    day2_meal_data = meal_plan.get("day2", [])
    print(meal_plan)
    return render_template("day2.html", meal_data=day2_meal_data, meal_plan_id=meal_plan_id)

@app.route("/day3")
def day3():
    meal_plan_id = request.args.get("meal_plan_id")
    meal_plan_entry = db.session.get(MealPlan, meal_plan_id)
    meal_plan = meal_plan_entry.meal_data if meal_plan_entry else {}
    day3_meal_data = meal_plan.get("day3", [])
    print(meal_plan)
    return render_template("day3.html", meal_data=day3_meal_data, meal_plan_id=meal_plan_id)
@app.route("/day4")
def day4():
    meal_plan_id = request.args.get("meal_plan_id")
    meal_plan_entry = db.session.get(MealPlan, meal_plan_id)
    meal_plan = meal_plan_entry.meal_data if meal_plan_entry else {}
    day4_meal_data = meal_plan.get("day4", [])
    print(meal_plan)
    return render_template("day4.html", meal_data=day4_meal_data, meal_plan_id=meal_plan_id)

@app.route("/day5")
def day5():
    meal_plan_id = request.args.get("meal_plan_id")
    meal_plan_entry = db.session.get(MealPlan, meal_plan_id)
    meal_plan = meal_plan_entry.meal_data if meal_plan_entry else {}
    day5_meal_data = meal_plan.get("day5", [])
    return render_template("day5.html", meal_data=day5_meal_data, meal_plan_id=meal_plan_id)

@app.route("/day6")
def day6():
    meal_plan_id = request.args.get("meal_plan_id")
    meal_plan_entry = db.session.get(MealPlan, meal_plan_id)
    meal_plan = meal_plan_entry.meal_data if meal_plan_entry else {}
    day6_meal_data = meal_plan.get("day6", [])
    return render_template("day6.html", meal_data=day6_meal_data, meal_plan_id=meal_plan_id)
@app.route("/day7")
def day7():
    meal_plan_id = request.args.get("meal_plan_id")
    meal_plan_entry = db.session.get(MealPlan, meal_plan_id)
    meal_plan = meal_plan_entry.meal_data if meal_plan_entry else {}
    day7_meal_data = meal_plan.get("day7", [])
    return render_template("day7.html", meal_data=day7_meal_data, meal_plan_id=meal_plan_id)
if __name__ == '__main__':
    app.run(debug=True)


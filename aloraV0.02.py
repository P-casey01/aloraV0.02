from flask import Flask, request, render_template, session
import openai
import logging
import secrets


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

meal_plans = {}


app = Flask(__name__)
openai.api_key = "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"
app.secret_key = secrets.token_urlsafe(24)


def generate_meal_plan(goals, food_preferences, dietary_restrictions, age, gender, height, weight, time, activity_level, day_number):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": """Hello, behave as Alora, an AI dietitian giving a diet plan for the following person. Ensure you calculate the BMR using the provided information and take this into account when designing the plan. The meal plan must include a breakfast, a morning snack, lunch, an afternoon snack, and dinner. For each meal, include the meal name, ingredients with their amounts in grams, nutritional content, and instructions for preparation. Start the meal plan with the meal name, ensuring to separate each meal with '---'. Use the format: 'Meal Name:', 'Ingredients in grams:', 'Nutritional Content:', 'Instructions:'. Please ensure your response is well-structured."""},
            {"role": "user", "content": f"""I am {age} years old. I am a {gender} with a height of {height} cm who weighs {weight} kg. I have these dietary requirements: {dietary_restrictions}. I like to eat the following cuisines and types of foods: {food_preferences}. my activity level is: {activity_level}. My goals are {goals}. I would like to spend {time} cooking. Please provide a meal plan for day {day_number}. Start the meal plan with the meal name, ensuring to separate each meal with '---'. Use the format: 'Meal Name:', 'Ingredients in grams:', 'Nutritional Content:', 'Instructions:'. Please ensure your response is well-structured"""}
        ],
        max_tokens=2048,
        n=2,
        temperature=0.5,
        timeout=900,
    )
 # Choose the response that meets your desired criteria
    selected_response = None
    max_meal_names = 0
    for choice in response.choices:
        # Extract the assistant's reply
        assistant_reply = choice.message['content']

        # Count the meal names in the reply
        meal_names = assistant_reply.count("Meal Name:")

        # Check if the reply has more meal names than the current best response
        if meal_names > max_meal_names:
            max_meal_names = meal_names
            selected_response = assistant_reply

        # If the reply has all meal names, break the loop
        if max_meal_names == 5:
            break

    # If no response meets the criteria, return the first one as a fallback
    if not selected_response:
        selected_response = response.choices[0].message['content']

    return selected_response.strip()


import re

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
    age = int(request.form.get("age", 0))
    gender = request.form.get("gender", "")
    height = int(request.form.get("height", 0))
    weight = int(request.form.get("weight", 0))
    time = request.form.get("time", "")
    activity_level = request.form.get("activity-level", "")

    meal_plan = {}
    for day in range(1, 8):
        daily_meal_data = generate_meal_plan(goals, food_preferences, dietary_restrictions, age, gender, height, weight, time, activity_level, day)
        daily_meals = parse_meal_data(daily_meal_data)
        meal_plan[f"day{day}"] = daily_meals
        
        
        
   #check input to ensure correct parsing     
    for day in range(1, 8):
        daily_meal_data = generate_meal_plan(goals, food_preferences, dietary_restrictions, age, gender, height, weight, time, activity_level, day)
        daily_meals = parse_meal_data(daily_meal_data)
        print(f"API Response for day{day}:")
        print(daily_meal_data)
        print(f"Parsed meals for day{day}:")
        print(daily_meals)
    
    meal_plan_id = secrets.token_urlsafe(8)
    meal_plans[meal_plan_id] = meal_plan


    
    day1_meal_data = meal_plan["day1"]


    return render_template("day1.html", meal_data=day1_meal_data, meal_plan_id=meal_plan_id)

@app.route("/day1")
def day1():
    meal_plan_id = request.args.get("meal_plan_id")
    meal_plan = meal_plans.get(meal_plan_id, {})
    day1_meal_data = meal_plan.get("day1", [])
    return render_template("day1.html", meal_data=day1_meal_data, meal_plan_id=meal_plan_id)

@app.route("/day2")
def day2():
    meal_plan_id = request.args.get("meal_plan_id")
    meal_plan = meal_plans.get(meal_plan_id, {})
    day2_meal_data = meal_plan.get("day2", [])
    return render_template("day2.html", meal_data=day2_meal_data, meal_plan_id=meal_plan_id)

@app.route("/day3")
def day3():
    meal_plan_id = request.args.get("meal_plan_id")
    meal_plan = meal_plans.get(meal_plan_id, {})
    day3_meal_data = meal_plan.get("day3", [])
    return render_template("day3.html", meal_data=day3_meal_data, meal_plan_id=meal_plan_id)
@app.route("/day4")
def day4():
    meal_plan_id = request.args.get("meal_plan_id")
    meal_plan = meal_plans.get(meal_plan_id, {})
    day4_meal_data = meal_plan.get("day4", [])
    return render_template("day4.html", meal_data=day4_meal_data, meal_plan_id=meal_plan_id)

@app.route("/day5")
def day5():
    meal_plan_id = request.args.get("meal_plan_id")
    meal_plan = meal_plans.get(meal_plan_id, {})
    day5_meal_data = meal_plan.get("day5", [])
    return render_template("day5.html", meal_data=day5_meal_data, meal_plan_id=meal_plan_id)
@app.route("/day6")
def day6():
    meal_plan_id = request.args.get("meal_plan_id")
    meal_plan = meal_plans.get(meal_plan_id, {})
    day6_meal_data = meal_plan.get("day6", [])
    return render_template("day6.html", meal_data=day6_meal_data, meal_plan_id=meal_plan_id)

@app.route("/day7")
def day7():
    meal_plan_id = request.args.get("meal_plan_id")
    meal_plan = meal_plans.get(meal_plan_id, {})
    day7_meal_data = meal_plan.get("day7", [])
    return render_template("day7.html", meal_data=day7_meal_data, meal_plan_id=meal_plan_id)

if __name__ == "__main__":
    app.run(debug=True)
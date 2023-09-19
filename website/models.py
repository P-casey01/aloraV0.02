from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    details = db.relationship("User_details", back_populates="user", uselist=False)
    meal_plans = db.relationship("MealPlan", backref="user")  # Define the relationship with MealPlan


class User_details(db.Model, UserMixin):     # DB table for user details
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Add this line to create a foreign key relationship
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    activity_level = db.Column(db.String(50))
    goals = db.Column(db.String(50))
    dietary_restrictions = db.Column(db.String(200))  # Add this line
    food_preferences = db.Column(db.String(200))  # Add this line
    time_spent_cooking = db.Column(db.String(50))  # Add this line
    user = db.relationship("User", back_populates="details")   # Add this line to establish the relationship

class MealPlan(db.Model):
    __tablename__ = "meal_plans"

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    meal_data = db.Column(db.JSON)

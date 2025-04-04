import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///weather_dashboard.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-development-only')
    
    # Task processing configuration
    TASK_DELAY_SECONDS = 5  # Simulated delay for task processing
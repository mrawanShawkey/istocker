import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///./database.db')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'SOME KEY')
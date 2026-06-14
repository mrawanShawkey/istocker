import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///./database.db')
    JWT_SECRET_KEY = os.environ.get('SECRET_KEY', 'SOME KEY')
    STMP_SERVER = os.environ.get('STMP_SERVER')
    STMP_PORT = os.environ.get('STMP_PORT')
    EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# 1. Initialize without the 'app' yet
bcrypt = Bcrypt()
jwt = JWTManager()
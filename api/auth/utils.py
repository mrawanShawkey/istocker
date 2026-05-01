from flask import request, Bcrypt, jwt

##Password Hashing (bcrypt.hash)
def hash_password(password):
    pass

##Verify Password (bcrypt.compare)
def verify_password(password):
    pass

##Access Token (jwt.sign) - KEYS??
def create_access_token(payload):
    pass

##Refresh Token (jwt.sign)
def create_refresh_token(payload):
    pass

##Get Token from Request (headers, split)
def get_user_token(header):
    pass

##Verify Token (jwt.verify)
def verify_token(token):
    pass
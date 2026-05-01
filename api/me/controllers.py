from flask import request
import me.services as Services

def get_me():
    return Services.get_me()

def edit_profile():
    data = request.get_json()
    return Services.edit_profile()

def edit_preferences():
    data = request.get_json()
    return Services.edit_preferences()

def get_results():
    return Services.get_results()
from flask import request
import questions.services as Services

def get_questions():
    type = request.args.get('type')
    return Services.get_questions(type)

def submit_responses():
    data = request.get_json()
    return Services.submit_responses()

def edit_responses():
    data = request.get_json()
    return Services.edit_responses()
from flask import request, Blueprint
import questions.controllers as Controllers

questions = Blueprint('questions', __name__)

@questions.route('/')
def get_questions():
    return Controllers.get_questions()

@questions.route('/responses', methods=['POST', 'PATCH'])
def responses():
    if request.method == 'POST':
        return Controllers.submit_responses()
    if request.method == 'PATCH':
        return Controllers.edit_responses()

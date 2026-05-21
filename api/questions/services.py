from flask import jsonify
import api.repositories as Repos
import api.common.errors.errors as Errors

def get_questions(type):
    if type == 'Registration':
        return Repos.get_registration_q_and_r()
    elif type == 'Questionnaire':
        return Repos.questionnaire_q_and_r()
    else:
        raise Errors.MissingQuestionType

def submit_responses():
    if type == 'Registration':
        return Repos.submit_registration_responses()
    elif type == 'Questionnaire': #risk profiling logic
        pass
    else:
        raise Errors.MissingQuestionType

def edit_responses():
    pass
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import questions.services as Services
import api.common.errors.errors as Errors

questions = Blueprint('questions', __name__)

@questions.route('/')
def get_questions():
    type = request.args.get('type')
    if not type:
        raise Errors.MissingQuestionType
    data = Services.get_questions(type)
    response = {
        'success': True,
        'data': data,
        'message': f'{type} questions returned in both languages.'
    }
    return jsonify(response), 200

@questions.route('/responses', methods=['POST'])
def submit_responses():
    type = request.args.get('type')
    if not type:
        raise Errors.MissingQuestionType
    payload = request.get_json()
    data = Services.submit_responses(type, payload)
    if type == 'Registration':
        message = 'Rsponses saved.'
    else:
        message = 'Responses saved. Risk profile and top 3 recommended stocks returned.'
    response = {
        'success': True,
        'data': data, 
        'message': message
    }
    return jsonify(response), 200

@questions.route('/responses', methods=['PATCH'])
@jwt_required()
def edit_responses():
    payload = request.get_json()
    Services.edit_responses(payload)
    response = {
        'success': True,
        'data': None,
        'message': 'Responses updated.'
    }
    return jsonify(response), 200
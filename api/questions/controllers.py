from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import api.questions.services as Services
import api.common.errors.errors as Errors

questions = Blueprint('questions', __name__)

@questions.route('/')
@jwt_required()
def get_questions():
    q_type = request.args.get('type')
    if not q_type:
        raise Errors.MissingQuestionType
    data = Services.get_questions(q_type)
    response = {
        'success': True,
        'data': data,
        'message': f'{q_type} questions returned in both languages.'
    }
    return jsonify(response), 200

@questions.route('/responses', methods=['POST'])
@jwt_required()
def submit_responses():
    q_type = request.args.get('type')
    if not q_type:
        raise Errors.MissingQuestionType
    payload = request.get_json()
    if not payload or 'responses' not in payload or not isinstance(payload['responses'], list):
        raise Errors.ValidationFailed
    reponses = payload['responses']
    uuid = get_jwt_identity()
    data = Services.submit_responses(uuid, q_type, reponses)
    if q_type == 'Registration':
        message = 'Responses saved.'
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
    if not payload:
        message = 'No updates were made.'
    elif 'editedResponses' not in payload:
        raise Errors.ValidationFailed
    elif isinstance(payload['editedResponses'], list) and len(payload['editedResponses']) == 0:
        message = 'No updates were made.'
    else:
        uuid = get_jwt_identity()
        edited_responses = payload['editedResponses']
        Services.edit_responses(uuid, edited_responses)
        message = 'Responses updated.'
    response = {
        'success': True,
        'data': None,
        'message': message
    }
    return jsonify(response), 200
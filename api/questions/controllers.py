from flask import Blueprint, request, jsonify
import questions.services as Services

questions = Blueprint('questions', __name__)

@questions.route('/')
def get_questions():
    type = request.args.get('type')
    response = Services.get_questions(type)
    return jsonify(response), 200

@questions.route('/responses', methods=['POST'])
def submit_responses():
    payload = request.get_json()
    response = Services.submit_responses(payload)
    return jsonify(response), 200

@questions.route('/responses', methods=['PATCH'])
def edit_responses():
    payload = request.get_json()
    response = Services.edit_responses(payload)
    return jsonify(response), 200
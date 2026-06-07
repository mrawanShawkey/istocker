from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import api.recommendations.services as Services
import api.common.errors.errors as Errors
from api.common.utils.utils import *

recommendations = Blueprint('recommendations', __name__)

@recommendations.route('/')
@jwt_required()
def get_recommendations():
    uuid = get_jwt_identity()
    data = Services.get_recommendations(uuid)
    if data:
        message = 'User recommendations returned.'
    else:
        message = 'Take questionnaire to view recommendations'
    response = {
        'success': True,
        'data': data,
        'message': message
    }
    return jsonify(response), 200
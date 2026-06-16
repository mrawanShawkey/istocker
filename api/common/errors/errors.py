from api.common.errors.app_errors import AppErrors
from api.common.extentions.extentions import jwt
import api.auth.repositories as Repos
from flask import jsonify

# AUTHORIZATION ERRORS
@jwt.unauthorized_loader
def unauthorized_callback(error_string):
    response = {
        'success': False,
        'code': 'UNAUTHORIZED',
        'message': 'You need to be logged in to access this resource'
    }
    return jsonify(response), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    response = {
        'success': False,
        'code': 'TOKEN_EXPIRED',
        'message': 'Your session has timed out.'
    }
    return jsonify(response), 401

@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    response = {
        'success': False,
        'code': 'TOKEN_INVALID',
        'message': 'Your token has been tampered with or is malformed.'
    }
    return jsonify(response), 401

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = Repos.is_token_revoked(jti)
    return token

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    response = {
        'success': False,
        'code': 'TOKEN_REVOKED',
        'message': 'Your session has timed out.'
    }
    return jsonify(response), 401

#AUTHENTICATION ERRORS
UserAlreadyExists = AppErrors(409, 'USER_ALREADY_EXISTS', 'This email is reserved for an existing user. Try logging in or signing up with a different email.', True)
IncorrectCredentials = AppErrors(401, 'INCORRECT_CREDENTIALS', 'Incorrect email or password.', True)

#INPUT / PARAMS ERRORS
InvalidInput = AppErrors(400, 'INVALID_INPUT', 'The request body is missing required fields.', True)
ValidationFailed = AppErrors(422, 'VALIDATION_FAILED', 'Your input is incorrectly formatted. Please check your input and try again.', True)
MissingQuestionType = AppErrors(400, 'MISSING_QUESTION_TYPE', 'The question type is missing or incorrect.', True)

#NOT FOUND ERRORS
MarketDataUnavailable = AppErrors(404, 'MARKET_DATA_UNAVAILABLE', 'Market data is currently unavailable. Please try again later.', True)
TickerNotFound = AppErrors(404, 'TICKER_NOT_FOUND', 'The ticker symbol is missing or does not exist. Please choose one from the existing list of tickers.', True)
ResultsNotFound = AppErrors(404, 'RESULTS_NOT_FOUND', 'Please answer the questionnaire to view risk scores and reommendations.', True)
UserNotFound = AppErrors(404, 'USER_NOT_FOUND', 'User does not exist.')

#DATABASE ERRORS
RecordNotFound = AppErrors(400, 'RECORD_NOT_FOUND', 'Target record does not exist.')
DatabaseError = AppErrors(500, 'DATABASE_ERROR', 'An unexpected database error occurred while updating responses.')

#CONNECTION ERRORS
LostConnection = AppErrors(500, 'LOST_CONNECTION', 'Could not connect to the requested resource. Please try again later.')
from api.common.errors.app_errors import AppErrors
from api.common.extentions.extentions import jwt

#AUTHENTICATION ERRORS
UserAlreadyExists = AppErrors(409, 'USER_ALREADY_EXISTS', 'This email is reserved for an existing user. Try logging in or signing up with a different email.', True)
IncorrectCredentials = AppErrors(401, 'INCORRECT_CREDENTIALS', 'Incorrect email or password.', True)

#AUTHORIZATION ERRORS
@jwt.unauthorized_loader
def unauthorized(error_string):
    raise AppErrors(401, 'UNAUTHORIZED', 'You need to be logged in to access this resource', True)
@jwt.expired_token_loader
def token_expired(error_string):
    raise AppErrors(401, 'TOKEN_EXPIRED', 'Your session has timed out.', True)
@jwt.invalid_token_loader
def invalid_token(error_string):
    raise AppErrors(401, 'TOKEN_INVALID', 'Your token has been tampered with.', True)
@jwt.token_in_blocklist_loader
def token_in_block(error_string):
    raise AppErrors(401, 'TOKEN_EXPIRED', 'Your session has timed out.', True)

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
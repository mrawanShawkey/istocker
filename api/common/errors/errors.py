from .app_errors import AppErrors

TokenExpired = AppErrors(401, 'TOKEN_EXPIRED', 'Your session has timed out.')
TokenInvalid = AppErrors(401, 'TOKEN_INVALID', 'Your token has been tampered with.')
Unauthorized = AppErrors(401, 'UNAUTHORIZED', 'You need to be logged in to access this resource')

InvalidInput = AppErrors(400, 'INVALID_INPUT', 'The request body is missing required fields.')
ValidationFailed = AppErrors(422, 'VALIDATION_FAILES', 'Your input is incorrectly formatted. Please check your input and try again.')

AlreadyExists = AppErrors(409, 'ALREADY_EXISTS', 'This email is reserved for an existing user. Try logging in or signing up with a different email.')
IncorrectCredentials = AppErrors(401, 'INCORRECT_CREDENTIALS', 'Incorrect email or password.')

TickerNotFound = AppErrors(404, 'TICKER_NOT_FOUND', 'The requested ticker does not exist. Please choose one from the existing list of tickers.')

ResultsNotFound = AppErrors(404, 'RESULTS_NOT_FOUND', 'Please answer the questionnaire to view risk scores and reommendations.')

MissingQuestionType = AppErrors(400, 'MISSING_QUESTION_TYPE', 'The question type is missing from the query params.')
from api.common.errors.app_errors import AppErrors

TokenExpired = AppErrors(401, 'Your session has timed out.')
TokenInvalid = AppErrors(401, 'Your token has been tampered with.')
Unauthorized = AppErrors(401, 'You need to be logged in to access this resource')

InvalidInput = AppErrors(400, 'The request body is missing required fields.')
ValidationFailed = AppErrors(422, 'Your input is incorrectly formatted. Please check your input and try again.')

ResultsNotFound = AppErrors(404, 'Please answer the questionnaire to view risk scores and reommendations.')
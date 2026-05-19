from flask import jsonify
from logs.logs import error_logger

def handle_error(err):
    message = getattr(err, 'message', 'Something went wrong.')
    code = getattr(err, 'code', 'SERVER_ERROR')
    status_code = getattr(err, 'status_code', 500)
    error_logger.log(status_code, code, message)

    if (err.isOperational):
        response = {
            'success': False,
            'code': code,
            'message': message 
        }
    else:
        status_code = 500
        response = {
            'success': False,
            'code': code,
            'message': message
        }
    return jsonify(response), err.status_code
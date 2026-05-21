from flask import jsonify
from api.common.logs.logs import error_logger

def handle_error(err):
    message = getattr(err, 'message', 'Something went wrong.')
    code = getattr(err, 'code', 'SERVER_ERROR')
    status_code = getattr(err, 'status_code', 500)
    error_logger.log(status_code, code, message)

    if (err.is_operational):
        response = {
            'success': False,
            'code': code,
            'message': message 
        }
    else:
        response = {
            'success': False,
            'code': code,
            'message': message
        }
    return jsonify(response), status_code
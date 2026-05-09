from flask import request
from logs.logs import error_logger

def handle_error(err, req, res):
    error_logger.log(err.message)

    if (err.isOperational == True):
        pass


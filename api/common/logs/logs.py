from datetime import datetime
from flask import jsonify
from config.paths import ERROR_LOGS

class Log:
    def __init__(self):
        self.file = open(ERROR_LOGS, 'a')
    
    def log(self, status_code, code, message):
        timestamp = datetime.now()
        log_entry = f'[{timestamp}]: {status_code} {code} {message}'
        self.file.write(jsonify(log_entry) + '\n')
        self.file.flush()

error_logger = Log()
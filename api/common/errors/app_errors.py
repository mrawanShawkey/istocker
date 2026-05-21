class AppErrors(Exception):
    def __init__(self, status_code, code, message, is_operational = False):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.is_operational = is_operational
    
    def __str__(self):
        return f'[{self.status_code}] {self.message}'
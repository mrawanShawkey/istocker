class AppErrors(Exception):
    def __init__(self, message, status_code = 500, is_operational = True):
        super().__init__(message)
        self.status_code = status_code
        self.is_operational = is_operational
    
    def __str__(self):
        return f'[{self.status_code}] {self.message}'
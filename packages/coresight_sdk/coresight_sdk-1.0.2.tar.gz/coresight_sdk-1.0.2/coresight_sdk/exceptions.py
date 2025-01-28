class ApiException(Exception):
    def __init__(self, status_code: int, message: str, details: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}

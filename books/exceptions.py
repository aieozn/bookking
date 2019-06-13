class RequestCriticalException(Exception):
    def __init__(self, message):
        self.message = message


class LoadBookException(Exception):
    def __init__(self, message):
        self.message = message

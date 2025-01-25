class Notfound(Exception):
    def __init__(self, message="Page or player not found."):
        super().__init__(message)

class NotLoaded(Exception):
    def __init__(self, message="The rosurces are not loaded."):
        super().__init__(message)
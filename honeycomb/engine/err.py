class BaseEngineError(Exception):
    """Base class for errors that should contatin information for the engine user"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"err {self.message}"

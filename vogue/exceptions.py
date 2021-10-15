from typing import Optional
from fastapi import status


class VogueError(Exception):
    def __init__(self, message: str):
        self.message = message


class MissingApplicationTag(Exception):
    pass


class VogueRestError(VogueError):
    def __init__(self, message: str, code: Optional[int] = None):
        self.message = message
        self.code = code
        super().__init__(message)


class InsertError(VogueRestError):
    def __init__(self, message: str, code: Optional[int] = status.HTTP_405_METHOD_NOT_ALLOWED):
        self.message = message
        self.code = code
        super().__init__(message, code)

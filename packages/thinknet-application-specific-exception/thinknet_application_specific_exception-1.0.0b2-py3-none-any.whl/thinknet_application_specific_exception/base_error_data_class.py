from enum import Enum
from typing import Type

class BaseErrorData(Enum):
    """
    Base Error class inherit from Enum with init function.

    Expected structure:
    - `exit_number`: An integer representing the code exit number.
    - `error_type`: The type of exception (e.g., ValueError, TypeError).
    - `error_message`: A human-readable string describing the error.
    """

    def __init__(self, exit_number: int, error_type: Type[BaseException], error_message: str):
        self.exit_number = exit_number
        self.error_type = error_type
        self.error_message = error_message

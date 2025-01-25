import traceback
from datetime import datetime
from typing import Dict, Any, Optional
import pytz

class ApplicationSpecificException(Exception):
    def __init__(
        self,
        error_code: str,
        exit_number: int,
        error_type_name: str,
        error_message: str,
        function_name: str,
        input_params: Dict[str, Any],
        parent: Optional["ApplicationSpecificException"] = None,
    ):
        self.timestamp = datetime.now(pytz.timezone("Asia/Bangkok")).strftime("%Y-%m-%d %H:%M:%S")
        self.error_code = error_code
        self.exit_number = exit_number
        self.error_type_name = error_type_name
        self.error_message = error_message
        self.function_name = function_name
        self.input_params = input_params
        self.parent = parent
        self.stack_trace = traceback.format_exc()

    def __str__(self, level: int = 0):
        indent = "  " * level
        result = (
            f"{indent}Error in {self.function_name}:\n"
            f"{indent}  Error Type: {self.error_type_name}\n"
            f"{indent}  Error Code: {self.error_code}\n"
            f"{indent}  Message: {self.error_message}\n"
            f"{indent}  Input Parameters: {self.input_params}\n"
        )
        if self.parent:
            result += f"{indent}Caused by:\n{self.parent.__str__(level + 1)}"
        if level == 0:
            result += f"Timestamp: {self.timestamp}\n"
            result += f"Stack Trace:\n{self.stack_trace}"
        return result

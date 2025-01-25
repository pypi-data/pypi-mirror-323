import sys
import os
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
import pytz
from thinknet_application_specific_exception.application_specific_exception_class import (
    ApplicationSpecificException,
)
from thinknet_application_specific_exception.base_error_data_class import BaseErrorData


def raise_error(
    error_data: BaseErrorData,
    input_params: Dict[str, Any],
    parent: Optional[ApplicationSpecificException] = None,
):
    if not isinstance(error_data, BaseErrorData):
        raise TypeError(
            f"Expected a BaseErrorCode instance, got {type(error_data).__name__}"
        )

    function_name = traceback.extract_stack()[-2].name
    exit_number = error_data.exit_number
    error_type_name = error_data.error_type.__name__
    error_message = error_data.error_message
    error_code = error_data.name

    raise ApplicationSpecificException(
        error_code,
        exit_number,
        error_type_name,
        error_message,
        function_name,
        input_params,
        parent
    )


def print_detailed_unexpected_error(e: Exception):
    current_time = datetime.now(pytz.timezone("Asia/Bangkok")).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    current_function_name = traceback.extract_stack()[-2].name
    print(f"Error occurred at: {current_time}")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print(f"Function Name: {current_function_name}")

    print("\nStack Trace:")
    traceback.print_exc()

    print("\nSystem Information:")
    print(f"Python Version: {sys.version}")
    print(f"Operating System: {os.name}")
    print(f"Platform: {sys.platform}")

    print("\nEnvironment Variables:")
    for key, value in os.environ.items():
        if key.startswith(("PYTHON", "PATH", "USER")):
            print(f"{key}: {value}")

    print("\nCurrent Working Directory:")
    print(os.getcwd())

"""AWS Lambda handler utilities for request/response handling and error management.

Provides structured request parsing and response formatting with error handling.
"""

import time
import traceback
from collections.abc import Callable
from functools import wraps
from typing import Any, Optional

from chainsaws.utils.error_utils.error_utils import AppError, make_error_description
from chainsaws.aws.lambda_client.event_handler.handler_models import (
    HandlerConfig,
    LambdaEvent,
    LambdaResponse,
)


def aws_lambda_handler(
    error_receiver: Optional[Callable[[str], Any]] = None,
    content_type: str = "application/json",
    use_traceback: bool = True,
    ignore_app_errors: Optional[list[AppError]] = None,
) -> Callable:
    """Decorator for AWS Lambda handlers with error handling and response formatting.

    Args:
        error_receiver: Callback function for error notifications
        content_type: Response content type
        use_traceback: Include traceback in error responses
        ignore_app_errors: List of AppErrors to ignore for notifications

    Example:
        @aws_lambda_handler(error_receiver=notify_slack)
        def handler(event, context):
            body = LambdaEvent.parse_obj(event).get_json_body()
            return {"message": "Success"}

    """
    config = HandlerConfig(
        error_receiver=error_receiver,
        content_type=content_type,
        use_traceback=use_traceback,
        ignore_app_errors=ignore_app_errors or [],
    )

    def decorator(func: Callable[..., Any]) -> Callable[..., dict]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> dict:
            start_time = time.time()
            event = args[0] if args else {}

            # API Gateway를 통한 호출인지 확인
            is_api_gateway = LambdaEvent.is_api_gateway_event(event)

            try:
                result = func(*args, **kwargs) or {}

                if isinstance(result, dict):
                    result.setdefault("rslt_cd", "S00000")
                    result.setdefault("rslt_msg", "Call Success")
                    result["duration"] = time.time() - start_time

                return LambdaResponse.create(
                    result,
                    status_code=200,
                    content_type=config.content_type,
                    serialize=is_api_gateway
                )

            except AppError as ex:
                result = {
                    "rslt_cd": ex.code,
                    "rslt_msg": ex.message,
                    "duration": time.time() - start_time,
                }

                if config.use_traceback:
                    result["traceback"] = str(traceback.format_exc())

                if config.error_receiver and ex.code not in {e.code for e in config.ignore_app_errors}:
                    try:
                        message = make_error_description(event)
                        config.error_receiver(message)
                    except Exception as err:
                        result["error_receiver_failed"] = str(err)

                return LambdaResponse.create(
                    result,
                    status_code=400,
                    content_type=config.content_type,
                    serialize=is_api_gateway
                )

            except Exception as ex:
                result = {
                    "rslt_cd": "S99999",
                    "rslt_msg": str(ex),
                    "duration": time.time() - start_time,
                }

                if config.use_traceback:
                    result["traceback"] = str(traceback.format_exc())

                if config.error_receiver:
                    try:
                        message = make_error_description(event, error=ex)
                        config.error_receiver(message)
                    except Exception as err:
                        result["error_receiver_failed"] = str(err)

                return LambdaResponse.create(
                    result,
                    status_code=500,
                    content_type=config.content_type,
                    serialize=is_api_gateway
                )

        return wrapper
    return decorator


def get_event_data(event: dict[str, Any]) -> LambdaEvent:
    """Get event data."""
    return LambdaEvent.model_validate(event)


def get_body(event: dict[str, Any]) -> dict[str, Any] | None:
    """Get JSON body from event."""
    return get_event_data(event).get_json_body()


def get_headers(event: dict[str, Any]) -> dict[str, str]:
    """Get request headers."""
    return get_event_data(event).headers


def get_source_ip(event: dict[str, Any]) -> str | None:
    """Get source IP address from event."""
    return get_event_data(event).requestContext.get_source_ip()

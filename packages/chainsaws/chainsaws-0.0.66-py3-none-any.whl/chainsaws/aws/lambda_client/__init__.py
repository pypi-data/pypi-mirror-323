"""AWS Lambda client for managing Lambda functions and providing structured logging.

This module provides:
1. Lambda Management:
   - Function creation and configuration
   - Function invocation and trigger management
   - Runtime and code management

2. Structured Logging:
   - JSON formatted logs
   - Lambda context injection
   - Correlation ID tracking
   - Cold start detection
   - Debug sampling

3. Event Handling:
   - API Gateway (REST/HTTP) event handling
   - ALB event handling
   - Request/Response formatting
   - Error handling with status codes
"""

from chainsaws.aws.lambda_client.lambda_client import LambdaAPI
from chainsaws.aws.lambda_client.lambda_models import (
    CreateFunctionRequest,
    FunctionCode,
    FunctionConfiguration,
    InvocationType,
    LambdaAPIConfig,
    LambdaHandler,
    PythonRuntime,
    TriggerType,
)
from chainsaws.aws.lambda_client.logger import (
    Logger,
    LogLevel,
    LogExtra,
    JsonPath,
    SampleRate,
)
from chainsaws.aws.lambda_client.types import Event, Context
from chainsaws.aws.lambda_client.event_handler import (
    aws_lambda_handler,
    APIGatewayRestResolver,
    APIGatewayHttpResolver,
    HttpMethod,
    Route,
    BaseResolver,
    Router,
    LambdaEvent,
    LambdaResponse,
    HandlerConfig,
    ALBEvent,
    ALBResponse,
    ALBResolver,
)

__all__ = [
    # Lambda Management
    "CreateFunctionRequest",
    "FunctionCode",
    "FunctionConfiguration",
    "InvocationType",
    "LambdaAPI",
    "LambdaAPIConfig",
    "LambdaHandler",
    "PythonRuntime",
    "TriggerType",
    "Event",
    "Context",

    # Structured Logging
    "Logger",
    "LogLevel",
    "LogExtra",
    "JsonPath",
    "SampleRate",

    # Event Handling
    "aws_lambda_handler",
    "APIGatewayRestResolver",
    "APIGatewayHttpResolver",
    "HttpMethod",
    "Route",
    "BaseResolver",
    "Router",
    "LambdaEvent",
    "LambdaResponse",
    "HandlerConfig",
    "ALBEvent",
    "ALBResponse",
    "ALBResolver",
]

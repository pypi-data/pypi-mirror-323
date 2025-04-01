from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from chainsaws.aws.shared.config import APIConfig


@dataclass
class LambdaAPIConfig(APIConfig):
    """Configuration for LambdaAPI."""


class InvocationType(str, Enum):
    """Lambda function invocation types."""

    REQUEST_RESPONSE = "RequestResponse"
    EVENT = "Event"
    DRY_RUN = "DryRun"


class PythonRuntime(str, Enum):
    """Supported Python runtimes for Lambda functions."""

    PYTHON_313 = "python3.13"
    PYTHON_312 = "python3.12"
    PYTHON_311 = "python3.11"
    PYTHON_310 = "python3.10"
    PYTHON_39 = "python3.9"


@dataclass
class LambdaHandler:
    """Lambda function handler configuration.

    Defaults to "index", "handler" # index.handler

    Example:
        handler = LambdaHandler(module_path="app", function_name="handler")  # app.handler
        handler = LambdaHandler(module_path="src.functions.app", function_name="process_event")  # src.functions.app.process_event
    """

    # Module path (e.g., 'app' or 'src.functions.app')
    module_path: str = "index"
    # Function name (e.g., 'handler' or 'process_event')
    function_name: str = "handler"

    def __post_init__(self) -> None:
        """Validate the handler configuration after initialization."""
        self._validate_python_identifier(self.module_path)
        self._validate_python_identifier(self.function_name)

    @staticmethod
    def _validate_python_identifier(value: str) -> None:
        """Validate that the path components are valid Python identifiers."""
        for part in value.split("."):
            if not part.isidentifier():
                msg = f"'{part}' is not a valid Python identifier"
                raise ValueError(msg)

    def __str__(self) -> str:
        return f"{self.module_path}.{self.function_name}"


@dataclass
class FunctionConfiguration:
    """Lambda function configuration."""

    function_name: str
    function_arn: str
    runtime: str
    role: str
    handler: str
    code_size: int
    timeout: int
    memory_size: int
    last_modified: str
    code_sha256: str
    version: str
    description: Optional[str] = None
    environment: Optional[dict[str, dict[str, str]]] = None
    tracing_config: Optional[dict[str, str]] = None
    revision_id: Optional[str] = None
    state: Optional[str] = None
    last_update_status: Optional[str] = None
    package_type: Optional[str] = None
    architectures: Optional[list[str]] = None


@dataclass
class FunctionCode:
    """Lambda function code configuration."""

    zip_file: Optional[bytes] = None
    s3_bucket: Optional[str] = None
    s3_key: Optional[str] = None
    s3_object_version: Optional[str] = None
    image_uri: Optional[str] = None


@dataclass
class CreateFunctionRequest:
    """Request model for creating Lambda function."""

    function_name: str
    runtime: PythonRuntime
    role: str
    handler: str
    code: FunctionCode
    timeout: int = field(default=3)
    memory_size: int = field(default=128)
    description: Optional[str] = None
    publish: bool = False
    environment: Optional[dict[str, dict[str, str]]] = None
    tags: Optional[dict[str, str]] = None
    architectures: list[str] = field(default_factory=lambda: ["x86_64"])

    def __post_init__(self) -> None:
        """Validate the function configuration after initialization."""
        if not 1 <= self.timeout <= 900:
            raise ValueError("Timeout must be between 1 and 900 seconds")
        if not 128 <= self.memory_size <= 10240:
            raise ValueError("MemorySize must be between 128 and 10240 MB")


class TriggerType(Enum):
    """Supported Lambda trigger types."""

    API_GATEWAY = "apigateway"
    S3 = "s3"
    EVENTBRIDGE = "eventbridge"
    SNS = "sns"
    SQS = "sqs"
    DYNAMODB = "dynamodb"

from datetime import datetime
from typing import Any, Optional


class AppError(Exception):
    """Base application error model."""

    def __init__(self, code: str, message: str, details: Optional[dict[str, Any]] = None):
        self.code = code
        self.message = message
        self.details = details
        self.timestamp = datetime.now()

    def __str__(self) -> str:
        """Convert error to string."""
        return f"AppError[{self.code}]: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "timestamp": self.timestamp,
            "details": self.details,
        }


class RequestIdentity:
    """Request identity information."""

    def __init__(self, source_ip: Optional[str] = None, user_agent: Optional[str] = None, user_arn: Optional[str] = None):
        self.source_ip = source_ip
        self.user_agent = user_agent
        self.user_arn = user_arn

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RequestIdentity":
        return cls(
            source_ip=data.get("sourceIp"),
            user_agent=data.get("userAgent"),
            user_arn=data.get("userArn")
        )


class RequestContext:
    """AWS request context."""

    def __init__(
        self,
        request_id: str,
        identity: RequestIdentity,
        stage: Optional[str] = None,
        path: Optional[str] = None,
        http_method: Optional[str] = None
    ):
        self.request_id = request_id
        self.identity = identity
        self.stage = stage
        self.path = path
        self.http_method = http_method

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RequestContext":
        return cls(
            request_id=data.get("requestId", ""),
            identity=RequestIdentity.from_dict(data.get("identity", {})),
            stage=data.get("stage"),
            path=data.get("path"),
            http_method=data.get("httpMethod")
        )


class ErrorEvent:
    """Error event with request context."""

    def __init__(
        self,
        request_context: RequestContext,
        body: Optional[str] = None,
        path_parameters: Optional[dict[str, str]] = None,
        query_string_parameters: Optional[dict[str, str]] = None
    ):
        self.request_context = request_context
        self.body = body
        self.path_parameters = path_parameters
        self.query_string_parameters = query_string_parameters

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ErrorEvent":
        return cls(
            request_context=RequestContext.from_dict(
                data.get("requestContext", {})),
            body=data.get("body"),
            path_parameters=data.get("pathParameters"),
            query_string_parameters=data.get("queryStringParameters")
        )


class ErrorDescription:
    """Structured error description."""

    def __init__(
        self,
        request_id: str,
        request_payload: str,
        error_traceback: str,
        source_ip: Optional[str] = None,
        cloudwatch_query: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        self.timestamp = timestamp or datetime.now()
        self.source_ip = source_ip
        self.request_id = request_id
        self.request_payload = request_payload
        self.error_traceback = error_traceback
        self.cloudwatch_query = cloudwatch_query

    def format(self) -> str:
        """Format error description for display in Slack."""
        description = f"""
*Timestamp:* {self.timestamp.isoformat()}
*Source IP:* {self.source_ip or 'unknown'}
*Request ID:* {self.request_id}

*Request Payload:*
```
{self.request_payload}
```

*Traceback:*
```
{self.error_traceback}
```
""".strip()

        return description

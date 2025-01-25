from enum import Enum
from typing import Any, Literal, Optional, TypedDict, Union

from pydantic import BaseModel, Field, field_validator
import datetime

from chainsaws.aws.shared.config import APIConfig


class APIGatewayV2APIConfig(APIConfig):
    """Configuration for API Gateway v2 API."""


class ProtocolType(str, Enum):
    """API Gateway v2 protocol types."""

    HTTP = "HTTP"
    WEBSOCKET = "WEBSOCKET"


class AuthorizationType(str, Enum):
    """API Gateway v2 authorization types."""

    NONE = "NONE"
    JWT = "JWT"
    AWS_IAM = "AWS_IAM"
    CUSTOM = "CUSTOM"


class IntegrationType(str, Enum):
    """API Gateway v2 integration types."""

    AWS_PROXY = "AWS_PROXY"  # For Lambda proxy
    HTTP_PROXY = "HTTP_PROXY"  # For HTTP proxy
    MOCK = "MOCK"  # For testing
    VPC_LINK = "VPC_LINK"  # For private integrations


class PayloadFormatVersion(str, Enum):
    """API Gateway v2 payload format versions."""

    VERSION_1_0 = "1.0"  # REST API compatibility
    VERSION_2_0 = "2.0"  # Optimized for HTTP APIs


class CorsConfig(BaseModel):
    """CORS configuration for HTTP APIs."""

    allow_origins: list[str] = Field(..., description="Allowed origins")
    allow_methods: list[str] = Field(..., description="Allowed HTTP methods")
    allow_headers: Optional[list[str]] = Field(
        None, description="Allowed headers")
    expose_headers: Optional[list[str]] = Field(
        None, description="Exposed headers")
    max_age: Optional[int] = Field(None, description="Max age in seconds")
    allow_credentials: Optional[bool] = Field(
        None, description="Whether to allow credentials")


class HttpApiConfig(BaseModel):
    """Configuration for creating an HTTP API."""

    name: str
    protocol_type: Literal[ProtocolType.HTTP] = ProtocolType.HTTP
    cors_configuration: Optional[CorsConfig] = Field(
        None, description="CORS configuration")
    disable_execute_api_endpoint: bool = Field(
        False, description="Whether to disable the default endpoint")
    description: Optional[str] = Field(None, description="API description")
    tags: Optional[dict[str, str]] = Field(None, description="Tags for the API")


class WebSocketApiConfig(BaseModel):
    """Configuration for creating a WebSocket API."""

    name: str
    protocol_type: Literal[ProtocolType.WEBSOCKET] = ProtocolType.WEBSOCKET
    route_selection_expression: str = Field(
        "$request.body.action",
        description="Route selection expression")
    api_key_selection_expression: Optional[str] = Field(
        None, description="API key selection expression")
    description: Optional[str] = Field(None, description="API description")
    tags: Optional[dict[str, str]] = Field(None, description="Tags for the API")


class RouteConfig(BaseModel):
    """Configuration for API route."""

    route_key: str = Field(..., description="Route key (e.g., 'GET /items')")
    target: str = Field(..., description="Integration target (e.g., Lambda ARN)")
    authorization_type: AuthorizationType = Field(
        AuthorizationType.NONE,
        description="Authorization type")
    authorizer_id: Optional[str] = Field(
        None, description="Authorizer ID if using custom authorizer")


class IntegrationConfig(BaseModel):
    """Configuration for v2 integration."""

    integration_type: IntegrationType
    integration_uri: Optional[str] = Field(
        None, description="Integration URI (e.g., Lambda ARN)")
    integration_method: Optional[str] = Field(
        None, description="Integration HTTP method")
    payload_format_version: PayloadFormatVersion = Field(
        PayloadFormatVersion.VERSION_2_0,
        description="Payload format version")
    timeout_in_millis: int = Field(
        30000, description="Integration timeout in milliseconds")
    credentials_arn: Optional[str] = Field(
        None, description="IAM role ARN for the integration")
    request_parameters: Optional[dict[str, str]] = Field(
        None, description="Request parameter mappings")
    response_parameters: Optional[dict[str, dict[str, str]]] = Field(
        None, description="Response parameter mappings")
    tls_config: Optional[dict[str, Any]] = Field(
        None, description="TLS configuration for integration")
    connection_id: Optional[str] = Field(
        None, description="VPC link ID for private integration")


class AuthorizerType(str, Enum):
    """API Gateway v2 authorizer types."""

    JWT = "JWT"
    LAMBDA = "REQUEST"  # REQUEST type for Lambda authorizer
    

class JwtConfig(BaseModel):
    """Configuration for JWT authorizer."""

    issuer: str = Field(..., description="JWT token issuer URL")
    audiences: list[str] = Field(..., description="List of allowed audiences")
    identity_source: list[str] = Field(
        ["$request.header.Authorization"],
        description="Where to extract the token from")


class LambdaAuthorizerConfig(BaseModel):
    """Configuration for Lambda authorizer."""

    function_arn: str = Field(..., description="Lambda function ARN")
    identity_sources: list[str] = Field(
        ..., description="Where to extract identity from")
    result_ttl: int = Field(300, description="Time to cache authorizer result")
    enable_simple_responses: bool = Field(
        True, description="Whether to enable simple IAM responses")
    payload_format_version: str = Field(
        "2.0", description="Authorizer payload version")


class VpcLinkConfig(BaseModel):
    """Configuration for VPC Link."""

    name: str = Field(..., description="VPC Link name")
    subnet_ids: list[str] = Field(..., description="Subnet IDs for the VPC link")
    security_group_ids: list[str] = Field(
        ..., description="Security group IDs")
    tags: Optional[dict[str, str]] = Field(None, description="Tags for VPC link")


class WebSocketMessageConfig(BaseModel):
    """Configuration for WebSocket message."""

    connection_id: str = Field(..., description="WebSocket connection ID")
    data: Union[str, dict[str, Any]] = Field(
        ..., description="Message data to send")
    
    @field_validator("data")
    @classmethod
    def validate_data(cls, v: Union[str, dict[str, Any]]) -> Union[str, dict[str, Any]]:
        """Validate message data."""
        if isinstance(v, (str, dict)):
            return v
        raise ValueError("Data must be either string or dictionary")


class CorsConfigurationResponse(TypedDict, total=False):
    """CORS configuration response."""

    AllowCredentials: bool
    AllowHeaders: list[str]
    AllowMethods: list[str]
    AllowOrigins: list[str]
    ExposeHeaders: list[str]
    MaxAge: int


class CreateApiResponse(TypedDict, total=False):
    """API Gateway v2 create_api response."""

    ApiEndpoint: str
    ApiGatewayManaged: bool
    ApiId: str
    ApiKeySelectionExpression: str
    CorsConfiguration: CorsConfigurationResponse
    CreatedDate: datetime
    Description: str
    DisableSchemaValidation: bool
    DisableExecuteApiEndpoint: bool
    ImportInfo: list[str]
    Name: str
    ProtocolType: Literal["WEBSOCKET", "HTTP"]
    RouteSelectionExpression: str
    Tags: dict[str, str]
    Version: str
    Warnings: list[str]


class IntegrationResponse(TypedDict, total=False):
    """Integration response."""

    ApiGatewayManaged: bool
    ConnectionId: str
    ConnectionType: str
    ContentHandlingStrategy: str
    CredentialsArn: str
    Description: str
    IntegrationId: str
    IntegrationMethod: str
    IntegrationResponseSelectionExpression: str
    IntegrationType: str
    IntegrationUri: str
    PassthroughBehavior: str
    PayloadFormatVersion: str
    RequestParameters: dict[str, str]
    RequestTemplates: dict[str, str]
    ResponseParameters: dict[str, dict[str, str]]
    TemplateSelectionExpression: str
    TimeoutInMillis: int
    TlsConfig: dict[str, Any]


class RouteResponse(TypedDict, total=False):
    """Route response."""

    ApiGatewayManaged: bool
    ApiKeyRequired: bool
    AuthorizationScopes: list[str]
    AuthorizationType: str
    AuthorizerId: str
    ModelSelectionExpression: str
    OperationName: str
    RequestModels: dict[str, str]
    RequestParameters: dict[str, dict[str, bool]]
    RouteId: str
    RouteKey: str
    RouteResponseSelectionExpression: str
    Target: str


class StageResponse(TypedDict, total=False):
    """Stage response."""

    AccessLogSettings: dict[str, str]
    ApiGatewayManaged: bool
    AutoDeploy: bool
    ClientCertificateId: str
    CreatedDate: datetime
    DefaultRouteSettings: dict[str, Any]
    DeploymentId: str
    Description: str
    LastDeploymentStatusMessage: str
    LastUpdatedDate: datetime
    RouteSettings: dict[str, Any]
    StageName: str
    StageVariables: dict[str, str]
    Tags: dict[str, str]


class AuthorizerResponse(TypedDict, total=False):
    """Authorizer response."""

    AuthorizerId: str
    AuthorizerCredentialsArn: str
    AuthorizerPayloadFormatVersion: str
    AuthorizerResultTtlInSeconds: int
    AuthorizerType: str
    AuthorizerUri: str
    EnableSimpleResponses: bool
    IdentitySource: list[str]
    IdentityValidationExpression: str
    JwtConfiguration: dict[str, Any]
    Name: str


class VpcLinkResponse(TypedDict, total=False):
    """VPC Link response."""

    CreatedDate: datetime
    Name: str
    SecurityGroupIds: list[str]
    SubnetIds: list[str]
    Tags: dict[str, str]
    VpcLinkId: str
    VpcLinkStatus: str
    VpcLinkStatusMessage: str
    VpcLinkVersion: str

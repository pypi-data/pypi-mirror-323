from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from chainsaws.aws.shared.config import APIConfig


class APIGatewayAPIConfig(APIConfig):
    """Configuration for API Gateway API."""


class EndpointType(str, Enum):
    """API Gateway endpoint types."""

    EDGE = "EDGE"
    REGIONAL = "REGIONAL"
    PRIVATE = "PRIVATE"


class IntegrationType(str, Enum):
    """API Gateway integration types."""

    AWS = "AWS"  # For AWS services
    AWS_PROXY = "AWS_PROXY"  # For Lambda proxy
    HTTP = "HTTP"  # For HTTP endpoints
    HTTP_PROXY = "HTTP_PROXY"  # For HTTP proxy
    MOCK = "MOCK"  # For testing


class HttpMethod(str, Enum):
    """HTTP methods supported by API Gateway."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    ANY = "ANY"


class RestAPIConfig(BaseModel):
    """Configuration for creating a REST API."""

    name: str
    description: Optional[str] = Field(None, description="API description")
    endpoint_type: EndpointType = Field(
        EndpointType.REGIONAL, description="API endpoint type")
    api_key_required: bool = Field(
        False, description="Whether API key is required")
    binary_media_types: Optional[list[str]] = Field(
        None, description="List of binary media types")
    minimum_compression_size: Optional[int] = Field(
        None, description="Minimum size in bytes for compression")
    tags: Optional[dict[str, str]] = Field(
        None, description="Tags for the API")


class ResourceConfig(BaseModel):
    """Configuration for API Gateway resource."""

    path_part: str = Field(..., description="Resource path segment")
    parent_id: Optional[str] = Field(
        None, description="Parent resource ID (None for root)")


class MethodConfig(BaseModel):
    """Configuration for API Gateway method."""

    http_method: HttpMethod
    authorization_type: str = Field("NONE", description="Authorization type")
    api_key_required: bool = Field(
        False, description="Whether API key is required")
    request_parameters: Optional[dict[str, bool]] = Field(
        None, description="Required request parameters")
    request_models: Optional[dict[str, str]] = Field(
        None, description="Request models for content types")


class IntegrationConfig(BaseModel):
    """Configuration for API Gateway integration."""

    type: IntegrationType
    uri: Optional[str] = Field(None, description="Integration endpoint URI")
    integration_http_method: Optional[str] = Field(
        None, description="HTTP method for integration")
    credentials: Optional[str] = Field(
        None, description="IAM role ARN for integration")
    request_parameters: Optional[dict[str, str]] = Field(
        None, description="Integration request parameters")
    request_templates: Optional[dict[str, str]] = Field(
        None, description="Integration request templates")
    passthrough_behavior: Optional[str] = Field(
        None, description="How to handle unmapped content types")
    cache_namespace: Optional[str] = Field(
        None, description="Integration cache namespace")
    cache_key_parameters: Optional[list[str]] = Field(
        None, description="Integration cache key parameters")
    content_handling: Optional[str] = Field(
        None, description="How to handle response payload")
    timeout_in_millis: Optional[int] = Field(
        None, description="Integration timeout in milliseconds")

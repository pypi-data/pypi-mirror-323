"""Functions for common AWS services usage, such as boto3 Session management."""
from typing import Any, ClassVar, Optional

import boto3
from pydantic import BaseModel, Field


class AWSCredentials(BaseModel):
    """AWS credentials configuration."""

    aws_access_key_id: Optional[str] = Field(
        default=None,
        description="AWS access key ID",
    )
    aws_secret_access_key: Optional[str] = Field(
        default=None,
        description="AWS secret access key",
    )
    region_name: Optional[str] = Field(
        default="ap-northeast-2",
        description="AWS region name",
    )
    profile_name: Optional[str] = Field(
        None,
        description="AWS profile name",
    )

    class Config:
        json_schema_extra: ClassVar[dict[str, Any]] = {
            "example": {
                "aws_access_key_id": "AKIAXXXXXXXXXXXXXXXX",
                "aws_secret_access_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                "region_name": "ap-northeast-2",
                "profile_name": "default",
            },
        }


def get_boto_session(credentials: Optional[AWSCredentials] = None) -> boto3.Session:
    """Returns a boto3 session. This function is wrapped to allow for future customization.

    Args:
        credentials (Optional[AWSCredentials]): Validated AWS credentials

    Returns:
        boto3.Session: Configured AWS session

    Warning:
        Using hardcoded credentials is not recommended for security reasons.
        Please use AWS IAM environment profiles instead.

    """
    if credentials:
        return boto3.Session(**credentials.model_dump(exclude_none=True))

    return boto3.Session()

"""Models for AWS SNS service.

This module contains Pydantic models representing various SNS entities and configurations.
These models provide type safety and validation for SNS operations.
"""

from datetime import datetime
from typing import Any, Dict, Optional, List, Tuple

from pydantic import BaseModel, Field

from chainsaws.aws.shared.config import APIConfig


class SNSAPIConfig(APIConfig):
    """Configuration for the SNS API.

    Attributes:
        credentials: AWS credentials.
        region: AWS region.
    """
    pass


class SNSMessageAttributes(BaseModel):
    """Message attributes for SNS messages.

    Attributes:
        string_value: The String value of the message attribute.
        binary_value: The Binary value of the message attribute.
        data_type: The data type of the message attribute.
    """
    string_value: Optional[str] = None
    binary_value: Optional[bytes] = None
    data_type: str = Field(default="String")


class SNSMessage(BaseModel):
    """Model representing an SNS message.

    Attributes:
        message: The message you want to send.
        subject: Optional subject for the message.
        message_attributes: Optional message attributes.
        message_structure: The structure of the message (json, string).
        message_deduplication_id: Token used for deduplication of sent messages.
        message_group_id: Tag that specifies that a message belongs to a specific group.
    """
    message: str
    subject: Optional[str] = None
    message_attributes: Optional[Dict[str, SNSMessageAttributes]] = None
    message_structure: Optional[str] = None
    message_deduplication_id: Optional[str] = None
    message_group_id: Optional[str] = None


class SNSTopic(BaseModel):
    """Model representing an SNS topic.

    Attributes:
        topic_arn: The ARN of the topic.
        topic_name: The name of the topic.
        display_name: The display name of the topic.
        policy: The topic's access policy.
        delivery_policy: The topic's delivery policy.
        tags: Tags associated with the topic.
    """
    topic_arn: str
    topic_name: str
    display_name: Optional[str] = None
    policy: Optional[Dict[str, Any]] = None
    delivery_policy: Optional[Dict[str, Any]] = None
    tags: Optional[Dict[str, str]] = None
    created_at: Optional[datetime] = None


class SNSSubscription(BaseModel):
    """Model representing an SNS subscription.

    Attributes:
        subscription_arn: The ARN of the subscription.
        topic_arn: The ARN of the topic.
        protocol: The subscription's protocol (http, https, email, sms, etc.).
        endpoint: The subscription's endpoint.
        raw_message_delivery: Whether to enable raw message delivery.
        filter_policy: The filter policy for the subscription.
    """
    subscription_arn: str
    topic_arn: str
    protocol: str
    endpoint: str
    raw_message_delivery: Optional[bool] = False
    filter_policy: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


class BatchPublishResult:
    """Result of a batch publish operation.

    Attributes:
        successful: List of successfully published message IDs.
        failed: List of failed messages with their error messages.
    """

    def __init__(self, results: List[Tuple[bool, str, Optional[str]]]) -> None:
        self.successful: List[str] = []
        self.failed: List[Tuple[SNSMessage, str]] = []

        for success, message_id, error in results:
            if success:
                self.successful.append(message_id)
            else:
                self.failed.append((message_id, error or "Unknown error"))

    @property
    def success_count(self) -> int:
        """Number of successfully published messages."""
        return len(self.successful)

    @property
    def failure_count(self) -> int:
        """Number of failed messages."""
        return len(self.failed)


class BatchSubscribeResult:
    """Result of a batch subscribe operation.

    Attributes:
        successful: List of successful subscription ARNs.
        failed: List of failed subscriptions with their error messages.
    """

    def __init__(self, results: List[Tuple[bool, str, Optional[str]]]) -> None:
        self.successful: List[str] = []
        self.failed: List[Tuple[Dict[str, Any], str]] = []

        for success, sub_arn, error in results:
            if success:
                self.successful.append(sub_arn)
            else:
                self.failed.append((sub_arn, error or "Unknown error"))

    @property
    def success_count(self) -> int:
        """Number of successful subscriptions."""
        return len(self.successful)

    @property
    def failure_count(self) -> int:
        """Number of failed subscriptions."""
        return len(self.failed)

from dataclasses import dataclass

from chainsaws.aws.shared.config import APIConfig


@dataclass
class STSAPIConfig(APIConfig):
    """Configuration for STS client."""


@dataclass
class AssumeRoleConfig:
    """Configuration for assuming an IAM role."""

    role_arn: str  # ARN of the role to assume
    role_session_name: str  # Identifier for the assumed role session
    # Duration of the session in seconds (900-43200)
    duration_seconds: int = 3600
    external_id: str | None = None  # Unique identifier for role assumption
    policy: dict | None = None  # IAM policy to further restrict the assumed role
    # Session tags to pass to the assumed role
    tags: dict[str, str] | None = None

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not 900 <= self.duration_seconds <= 43200:
            raise ValueError("duration_seconds must be between 900 and 43200")


@dataclass
class AssumedRoleCredentials:
    """Credentials for an assumed role."""

    access_key_id: str  # Temporary access key ID
    secret_access_key: str  # Temporary secret access key
    session_token: str  # Temporary session token
    expiration: str  # Timestamp when credentials expire


@dataclass
class GetCallerIdentityResponse:
    """Response from get-caller-identity."""

    account: str  # AWS account ID
    arn: str  # ARN of the caller
    user_id: str  # Unique identifier of the caller


@dataclass
class GetFederationTokenConfig:
    """Configuration for getting a federation token."""

    name: str  # Name of the federated user
    # Duration of the credentials in seconds (900-129600)
    duration_seconds: int = 43200
    policy: dict | None = None  # IAM policy for federated user
    tags: dict[str, str] | None = None  # Session tags for federated user

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not 900 <= self.duration_seconds <= 129600:
            raise ValueError("duration_seconds must be between 900 and 129600")


@dataclass
class FederationTokenCredentials:
    """Credentials for a federated user."""

    access_key_id: str  # Temporary access key ID
    secret_access_key: str  # Temporary secret access key
    session_token: str  # Temporary session token
    expiration: str  # Timestamp when credentials expire
    federated_user_arn: str  # ARN of the federated user
    federated_user_id: str  # ID of the federated user

from dataclasses import dataclass, field, fields
from typing import (
    Any,
    ClassVar,
    Literal,
    Self,
    TypedDict,
    TypeGuard,
    Union,
    Optional,
)
import json

from chainsaws.aws.shared.config import APIConfig


@dataclass
class KeySchemaElement:
    """DynamoDB key schema element."""

    attribute_name: str  # Name of the key attribute
    key_type: Literal["HASH", "RANGE"]  # Type of the key


@dataclass
class AttributeDefinitionElement:
    """DynamoDB attribute definition element."""

    attribute_name: str  # Name of the attribute
    attribute_type: Literal["S", "N", "B"]  # Type of the attribute


@dataclass
class StreamSpecificationElement:
    """DynamoDB stream specification."""

    stream_enabled: bool = True  # Enable/disable DynamoDB Streams
    stream_view_type: Literal["NEW_IMAGE", "OLD_IMAGE", "NEW_AND_OLD_IMAGES",
                              "KEYS_ONLY"] = "NEW_AND_OLD_IMAGES"  # Type of information captured in the stream


@dataclass
class CreateTableRequest:
    """Request model for creating a DynamoDB table."""

    table_name: str  # Name of the table to create
    # List of attributes that describe the key schema
    attribute_definitions: list[AttributeDefinitionElement]
    key_schema: list[KeySchemaElement]  # List of key schema elements
    # Billing mode for the table
    billing_mode: Literal["PROVISIONED", "PAY_PER_REQUEST"] = "PAY_PER_REQUEST"
    # DynamoDB Streams configuration
    stream_specification: Optional[StreamSpecificationElement] = None


@dataclass
class PartitionIndex:
    """Configuration for a partition index."""

    pk: str  # Primary key field for the index
    sk: str  # Sort key field for the index


@dataclass
class PartitionMapConfig:
    """Configuration for a single partition in the partition map."""

    pk: str  # Primary key field
    sk: str  # Sort key field
    uks: Optional[list[str]] = field(
        default_factory=list)  # List of unique key fields
    indexes: Optional[list[PartitionIndex]] = field(
        default_factory=list)  # List of secondary indexes


@dataclass
class PartitionMap:
    """Complete partition map configuration."""

    # Mapping of partition names to their configurations
    partitions: dict[str, PartitionMapConfig]


@dataclass
class DynamoDBConfig:
    """DynamoDB configuration settings."""

    region: str = "ap-northeast-2"  # AWS region for the DynamoDB table
    # Maximum number of connections in the connection pool
    max_pool_connections: int = 100

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not 1 <= self.max_pool_connections <= 1000:
            raise ValueError("max_pool_connections must be between 1 and 1000")


@dataclass
class DynamoDBAPIConfig(APIConfig):
    """DynamoDB API configuration."""

    # Maximum number of connections in the connection pool
    max_pool_connections: int = 100
    endpoint_url: Optional[str] = None  # Endpoint URL for the DynamoDB API

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        super().__post_init__()
        if not 1 <= self.max_pool_connections <= 1000:
            raise ValueError("max_pool_connections must be between 1 and 1000")


# Filter condition types
FilterCondition = Literal[
    "eq", "neq", "lte", "lt", "gte", "gt", "btw",
    "stw", "is_in", "contains", "exist", "not_exist",
]


class FilterDict(TypedDict):
    """Single filter condition."""

    field: str
    value: Any
    condition: FilterCondition


class RecursiveFilterBase(TypedDict):
    """Base for recursive filter operations."""

    field: str
    value: Any
    condition: FilterCondition


class RecursiveFilterNode(TypedDict):
    """Node in recursive filter tree."""

    left: Union["RecursiveFilterNode", RecursiveFilterBase]
    operation: Literal["and", "or"]
    right: Union["RecursiveFilterNode", RecursiveFilterBase]


class DynamoIndex:
    """Index configuration for DynamoDB models."""

    def __init__(self, pk: str, sk: str) -> None:
        self.pk = pk
        self.sk = sk


class DynamoDBPartitionConfig:
    """Partition configuration for DynamoDB models."""

    def __init__(
        self,
        partition: str,
        pk_field: str,
        sk_field: str,
        indexes: list[DynamoIndex] | None = None,
    ) -> None:
        self.partition = partition
        self.pk_field = pk_field
        self.sk_field = sk_field
        self.indexes = indexes or []


@dataclass
class DynamoModel:
    """Base model for DynamoDB models with partition configuration."""

    # System fields with aliases
    _id: Optional[str] = field(default=None, metadata={"exclude": True})
    _crt: Optional[int] = field(default=None, metadata={"exclude": True})
    _ptn: Optional[str] = field(default=None, metadata={"exclude": True})

    # Class variables for configuration
    _partition: ClassVar[str]
    _pk: ClassVar[str]
    _sk: ClassVar[str]
    _indexes: ClassVar[list[DynamoIndex]] = []

    # TTL field
    _ttl: ClassVar[Optional[float]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the model to a dictionary."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def to_json(self) -> str:
        """Convert the model to a JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create a model instance from a dictionary."""
        # Filter out unknown fields
        known_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)

    @staticmethod
    def is_dynamo_model(model: type[Any]) -> TypeGuard[type["DynamoModel"]]:
        """Check if a type is a DynamoModel."""
        return (
            isinstance(model, type)
            and issubclass(model, DynamoModel)
            and hasattr(model, "_partition")
            and hasattr(model, "_pk")
            and hasattr(model, "_sk")
        )

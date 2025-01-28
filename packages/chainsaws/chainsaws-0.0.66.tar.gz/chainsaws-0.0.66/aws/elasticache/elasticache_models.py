from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict


class EngineType(str, Enum):
    """Supported cache engine types."""
    REDIS = "redis"
    MEMCACHED = "memcached"
    VALKEY = "valkey"


@dataclass
class NodeType:
    """Node type configuration."""
    instance_type: str  # Instance type (e.g., cache.r6g.xlarge)
    num_nodes: int  # Number of nodes in the cluster


@dataclass
class RedisConfig:
    """Redis specific configuration."""
    version: str  # Redis version
    auth_token: Optional[str] = None  # Authentication token
    cluster_mode_enabled: bool = False  # Enable cluster mode
    automatic_failover_enabled: bool = False  # Enable automatic failover


@dataclass
class MemcachedConfig:
    """Memcached specific configuration."""
    version: str  # Memcached version
    num_threads: int = 4  # Number of threads per node


@dataclass
class ValKeyConfig:
    """ValKey specific configuration."""
    version: str  # ValKey version
    auth_token: str  # Authentication token
    enhanced_io: bool = False  # Enable enhanced I/O
    tls_offloading: bool = False  # Enable TLS offloading
    enhanced_io_multiplexing: bool = False  # Enable enhanced I/O multiplexing


@dataclass
class SubnetGroup:
    """Subnet group configuration."""
    name: str  # Subnet group name
    subnet_ids: List[str]  # List of subnet IDs


@dataclass
class SecurityGroup:
    """Security group configuration."""
    id: str  # Security group ID
    name: Optional[str] = None  # Security group name


@dataclass
class ServerlessScalingConfiguration:
    """Serverless scaling configuration."""

    # Minimum capacity in ElastiCache Capacity Units (ECU)
    minimum_capacity: float = 0.5
    # Maximum capacity in ElastiCache Capacity Units (ECU)
    maximum_capacity: float = 100.0

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not 0.5 <= self.minimum_capacity <= 100.0:
            raise ValueError("minimum_capacity must be between 0.5 and 100.0")
        if not 0.5 <= self.maximum_capacity <= 100.0:
            raise ValueError("maximum_capacity must be between 0.5 and 100.0")
        if self.minimum_capacity > self.maximum_capacity:
            raise ValueError(
                "minimum_capacity cannot be greater than maximum_capacity")


@dataclass
class CreateClusterRequest:
    """Request model for creating an ElastiCache cluster."""

    cluster_id: str  # Unique identifier for the cluster
    engine: EngineType  # Cache engine type
    node_type: NodeType  # Node type configuration
    redis_config: Optional[RedisConfig] = None  # Redis specific configuration
    # Memcached specific configuration
    memcached_config: Optional[MemcachedConfig] = None
    # ValKey specific configuration
    valkey_config: Optional[ValKeyConfig] = None
    subnet_group: Optional[SubnetGroup] = None  # Subnet group configuration
    security_groups: Optional[List[SecurityGroup]] = None  # Security groups
    tags: Dict[str, str] = field(default_factory=dict)  # Resource tags

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.cluster_id:
            raise ValueError("cluster_id is required")
        if self.engine == EngineType.REDIS and not self.redis_config:
            raise ValueError("redis_config is required for Redis engine")
        if self.engine == EngineType.MEMCACHED and not self.memcached_config:
            raise ValueError(
                "memcached_config is required for Memcached engine")
        if self.engine == EngineType.VALKEY and not self.valkey_config:
            raise ValueError("valkey_config is required for ValKey engine")

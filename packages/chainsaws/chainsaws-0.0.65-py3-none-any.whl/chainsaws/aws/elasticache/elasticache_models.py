"""ElastiCache API models."""

from typing import Any, ClassVar, Dict, List, Literal, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
from dataclasses import dataclass

from chainsaws.aws.shared.config import APIConfig


class ElastiCacheAPIConfig(APIConfig):
    """ElastiCache API configuration."""

    max_retries: int = Field(
        3,
        description="Maximum number of retry attempts",
        ge=0,
        le=10,
    )

    class Config:
        json_schema_extra: ClassVar[Dict[str, Any]] = {
            "example": {
                "credentials": {
                    "aws_access_key_id": "AKIAXXXXXXXXXXXXXXXX",
                    "aws_secret_access_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                    "region_name": "ap-northeast-2",
                },
                "max_retries": 3,
            },
        }


# General Purpose
GeneralPurposeNodeType = Literal[
    # M7g
    "cache.m7g.large", "cache.m7g.xlarge", "cache.m7g.2xlarge", "cache.m7g.4xlarge",
    "cache.m7g.8xlarge", "cache.m7g.12xlarge", "cache.m7g.16xlarge",
    # M6g
    "cache.m6g.large", "cache.m6g.xlarge", "cache.m6g.2xlarge", "cache.m6g.4xlarge",
    "cache.m6g.8xlarge", "cache.m6g.12xlarge", "cache.m6g.16xlarge",
    # M5
    "cache.m5.large", "cache.m5.xlarge", "cache.m5.2xlarge", "cache.m5.4xlarge",
    "cache.m5.12xlarge", "cache.m5.24xlarge",
    # M4
    "cache.m4.large", "cache.m4.xlarge", "cache.m4.2xlarge", "cache.m4.4xlarge",
    "cache.m4.10xlarge",
    # T4g
    "cache.t4g.micro", "cache.t4g.small", "cache.t4g.medium",
    # T3
    "cache.t3.micro", "cache.t3.small", "cache.t3.medium",
    # T2
    "cache.t2.micro", "cache.t2.small", "cache.t2.medium"
]

# Memory Optimized
MemoryOptimizedNodeType = Literal[
    # R7g
    "cache.r7g.large", "cache.r7g.xlarge", "cache.r7g.2xlarge", "cache.r7g.4xlarge",
    "cache.r7g.8xlarge", "cache.r7g.12xlarge", "cache.r7g.16xlarge",
    # R6g
    "cache.r6g.large", "cache.r6g.xlarge", "cache.r6g.2xlarge", "cache.r6g.4xlarge",
    "cache.r6g.8xlarge", "cache.r6g.12xlarge", "cache.r6g.16xlarge",
    # R5
    "cache.r5.large", "cache.r5.xlarge", "cache.r5.2xlarge", "cache.r5.4xlarge",
    "cache.r5.12xlarge", "cache.r5.24xlarge",
    # R4
    "cache.r4.large", "cache.r4.xlarge", "cache.r4.2xlarge", "cache.r4.4xlarge",
    "cache.r4.8xlarge", "cache.r4.16xlarge"
]

# Memory Optimized with Data Tiering
MemoryOptimizedWithDataTieringNodeType = Literal[
    "cache.r6gd.xlarge", "cache.r6gd.2xlarge", "cache.r6gd.4xlarge",
    "cache.r6gd.8xlarge", "cache.r6gd.12xlarge", "cache.r6gd.16xlarge"
]

# Network Optimized
NetworkOptimizedNodeType = Literal[
    "cache.c7gn.large", "cache.c7gn.xlarge", "cache.c7gn.2xlarge", "cache.c7gn.4xlarge",
    "cache.c7gn.8xlarge", "cache.c7gn.12xlarge", "cache.c7gn.16xlarge"
]

# Serverless Configuration


class ServerlessScalingConfiguration(BaseModel):
    """Serverless scaling configuration."""

    minimum_capacity: float = Field(
        0.5,
        description="Minimum capacity in ElastiCache Capacity Units (ECU)",
        ge=0.5,
        le=100.0
    )
    maximum_capacity: float = Field(
        100.0,
        description="Maximum capacity in ElastiCache Capacity Units (ECU)",
        ge=0.5,
        le=100.0
    )

    class Config:
        json_schema_extra: ClassVar[Dict[str, Any]] = {
            "example": {
                "minimum_capacity": 0.5,
                "maximum_capacity": 4.0
            }
        }


# Serverless Cache Type
ServerlessType = Literal["serverless"]

# Combined node types including serverless
NodeInstanceType = Union[
    GeneralPurposeNodeType,
    MemoryOptimizedNodeType,
    MemoryOptimizedWithDataTieringNodeType,
    NetworkOptimizedNodeType,
    ServerlessType
]


@dataclass
class NodeType:
    """Node type configuration for ElastiCache clusters."""

    instance_type: NodeInstanceType
    num_nodes: int = 1
    serverless_config: Optional[ServerlessScalingConfiguration] = None

    def __post_init__(self):
        """Validate serverless configuration."""
        if self.instance_type == "serverless":
            if not self.serverless_config:
                self.serverless_config = ServerlessScalingConfiguration()
            self.num_nodes = 1  # Serverless always uses 1 node


class RedisConfig(BaseModel):
    """Redis specific configuration."""

    version: str = Field(..., description="Redis engine version")
    port: int = Field(6379, description="Port number")
    auth_token: Optional[str] = Field(
        None, description="Auth token for Redis AUTH")
    transit_encryption: bool = Field(
        True, description="Enable in-transit encryption")
    at_rest_encryption: bool = Field(
        True, description="Enable at-rest encryption")
    auto_failover: bool = Field(True, description="Enable auto-failover")
    multi_az: bool = Field(True, description="Enable Multi-AZ")
    backup_retention: int = Field(
        7, description="Backup retention period in days", ge=0, le=35)
    backup_window: Optional[str] = Field(
        None, description="Preferred backup window")
    maintenance_window: Optional[str] = Field(
        None, description="Preferred maintenance window")
    parameter_group: Optional[str] = Field(
        None, description="Cache parameter group")
    is_serverless: bool = Field(
        False, description="Whether this is a serverless configuration")


class MemcachedConfig(BaseModel):
    """Memcached specific configuration."""

    version: str = Field(..., description="Memcached engine version")
    port: int = Field(11211, description="Port number")
    parameter_group: Optional[str] = Field(
        None, description="Cache parameter group")


class SubnetGroup(BaseModel):
    """Subnet group configuration."""

    name: str = Field(..., description="The name of the subnet group")
    description: str = Field(...,
                             description="Description for the subnet group")
    subnet_ids: List[str] = Field(..., description="List of VPC subnet IDs")


class SecurityGroup(BaseModel):
    """Security group configuration."""

    id: str = Field(..., description="The ID of the security group")
    name: Optional[str] = Field(
        None, description="The name of the security group")


# Engine Types
EngineType = Literal["redis", "memcached", "valkey"]


class ValKeyConfig(BaseModel):
    """ValKey specific configuration."""

    version: str = Field(..., description="ValKey engine version")
    port: int = Field(6379, description="Port number")
    auth_token: Optional[str] = Field(
        None, description="Auth token for ValKey AUTH")
    transit_encryption: bool = Field(
        True, description="Enable in-transit encryption")
    at_rest_encryption: bool = Field(
        True, description="Enable at-rest encryption")
    auto_failover: bool = Field(True, description="Enable auto-failover")
    multi_az: bool = Field(True, description="Enable Multi-AZ")
    backup_retention: int = Field(
        7, description="Backup retention period in days", ge=0, le=35)
    backup_window: Optional[str] = Field(
        None, description="Preferred backup window")
    maintenance_window: Optional[str] = Field(
        None, description="Preferred maintenance window")
    parameter_group: Optional[str] = Field(
        None, description="Cache parameter group")
    enhanced_io: bool = Field(True, description="Enable Enhanced I/O")
    tls_offloading: bool = Field(True, description="Enable TLS Offloading")
    enhanced_io_multiplexing: bool = Field(
        True, description="Enable Enhanced I/O Multiplexing")

    class Config:
        json_schema_extra: ClassVar[Dict[str, Any]] = {
            "example": {
                "version": "1.0",
                "port": 6379,
                "auth_token": "my-auth-token",
                "enhanced_io": True,
                "tls_offloading": True,
                "enhanced_io_multiplexing": True
            }
        }


class CreateClusterRequest(BaseModel):
    """Request model for creating an ElastiCache cluster."""

    cluster_id: str = Field(...,
                            description="Unique identifier for the cluster")
    engine: EngineType = Field(..., description="Cache engine type")
    node_type: NodeType = Field(..., description="Node type configuration")
    redis_config: Optional[RedisConfig] = Field(
        None, description="Redis specific configuration")
    memcached_config: Optional[MemcachedConfig] = Field(
        None, description="Memcached specific configuration")
    valkey_config: Optional[ValKeyConfig] = Field(
        None, description="ValKey specific configuration")
    subnet_group: Optional[SubnetGroup] = Field(
        None, description="Subnet group configuration")
    security_groups: Optional[List[SecurityGroup]] = Field(
        None, description="Security groups")
    tags: Dict[str, str] = Field(
        default_factory=dict, description="Resource tags")

    class Config:
        json_schema_extra: ClassVar[Dict[str, Any]] = {
            "example": {
                "cluster_id": "my-valkey-cluster",
                "engine": "valkey",
                "node_type": {
                    "instance_type": "cache.r6g.xlarge",
                    "num_nodes": 2
                },
                "valkey_config": {
                    "version": "1.0",
                    "auth_token": "my-auth-token",
                    "enhanced_io": True,
                    "tls_offloading": True,
                    "enhanced_io_multiplexing": True
                },
                "tags": {
                    "Environment": "Production"
                }
            }
        }


class ClusterStatus(BaseModel):
    """ElastiCache cluster status information."""

    cluster_id: str = Field(..., description="The ID of the cache cluster")
    status: str = Field(..., description="Current status of the cluster")
    endpoint: Optional[str] = Field(None, description="Cluster endpoint")
    port: int = Field(..., description="Port number")
    node_type: str = Field(..., description="Node type")
    num_nodes: int = Field(..., description="Number of nodes")
    engine: str = Field(..., description="Cache engine type")
    engine_version: str = Field(..., description="Cache engine version")
    subnet_group: Optional[str] = Field(None, description="Subnet group name")
    security_groups: List[str] = Field(
        default_factory=list, description="Security group IDs")
    tags: Dict[str, str] = Field(
        default_factory=dict, description="Resource tags")


class ModifyClusterRequest(BaseModel):
    """Request model for modifying an ElastiCache cluster."""

    cluster_id: str = Field(..., description="The ID of the cache cluster")
    apply_immediately: bool = Field(
        False, description="Whether to apply changes immediately or during maintenance window"
    )
    node_type: Optional[NodeType] = Field(
        None, description="New node type configuration")
    security_groups: Optional[List[SecurityGroup]] = Field(
        None, description="New security groups"
    )
    maintenance_window: Optional[str] = Field(
        None, description="New maintenance window")
    engine_version: Optional[str] = Field(
        None, description="New engine version")
    auth_token: Optional[str] = Field(
        None, description="New auth token (Redis only)")
    tags: Optional[Dict[str, str]] = Field(
        None, description="New resource tags")


class SnapshotConfig(BaseModel):
    """Snapshot configuration."""

    snapshot_name: str = Field(..., description="The name of the snapshot")
    retention_period: int = Field(
        7, description="Number of days to retain the snapshot", ge=1, le=35
    )
    target_bucket: Optional[str] = Field(
        None, description="S3 bucket for exporting snapshot")


class RestoreClusterRequest(BaseModel):
    """Request model for restoring an ElastiCache cluster from snapshot."""

    snapshot_name: str = Field(...,
                               description="The name of the snapshot to restore from")
    target_cluster_id: str = Field(...,
                                   description="The ID for the new cluster")
    node_type: Optional[NodeType] = Field(
        None, description="New node type configuration")
    subnet_group: Optional[SubnetGroup] = Field(
        None, description="New subnet group")
    port: Optional[int] = Field(None, description="New port number")
    security_groups: Optional[List[SecurityGroup]] = Field(
        None, description="Security groups")
    tags: Dict[str, str] = Field(
        default_factory=dict, description="Resource tags")


class ParameterType(BaseModel):
    """Parameter type definition."""

    name: str = Field(..., description="Parameter name")
    value: Union[str, int, bool] = Field(..., description="Parameter value")
    data_type: Literal["string", "integer",
                       "boolean"] = Field(..., description="Parameter data type")
    modifiable: bool = Field(
        True, description="Whether the parameter can be modified")
    description: Optional[str] = Field(
        None, description="Parameter description")
    minimum_engine_version: Optional[str] = Field(
        None, description="Minimum engine version required")
    allowed_values: Optional[str] = Field(
        None, description="Allowed values for the parameter")


class CreateParameterGroupRequest(BaseModel):
    """Request model for creating a parameter group."""

    group_name: str = Field(..., description="The name of the parameter group")
    group_family: str = Field(...,
                              description="The family of the parameter group (e.g., redis6.x)")
    description: str = Field(...,
                             description="Description for the parameter group")
    parameters: Optional[Dict[str, Union[str, int, bool]]] = Field(
        None, description="Initial parameter values"
    )

    class Config:
        json_schema_extra: ClassVar[Dict[str, Any]] = {
            "example": {
                "group_name": "my-redis-params",
                "group_family": "redis6.x",
                "description": "Custom Redis parameters",
                "parameters": {
                    "maxmemory-policy": "volatile-lru",
                    "timeout": 0,
                    "notify-keyspace-events": "KEA",
                },
            },
        }


class ModifyParameterGroupRequest(BaseModel):
    """Request model for modifying parameters in a parameter group."""

    group_name: str = Field(..., description="The name of the parameter group")
    parameters: Dict[str, Union[str, int, bool]] = Field(
        ..., description="Parameters to modify"
    )

    class Config:
        json_schema_extra: ClassVar[Dict[str, Any]] = {
            "example": {
                "group_name": "my-redis-params",
                "parameters": {
                    "maxmemory-policy": "allkeys-lru",
                    "timeout": 300,
                },
            },
        }


class ParameterGroupStatus(BaseModel):
    """Parameter group status information."""

    group_name: str = Field(..., description="The name of the parameter group")
    group_family: str = Field(...,
                              description="The family of the parameter group")
    description: str = Field(...,
                             description="Description of the parameter group")
    parameters: Dict[str, ParameterType] = Field(
        default_factory=dict, description="Current parameter values"
    )

    class Config:
        json_schema_extra: ClassVar[Dict[str, Any]] = {
            "example": {
                "group_name": "my-redis-params",
                "group_family": "redis6.x",
                "description": "Custom Redis parameters",
                "parameters": {
                    "maxmemory-policy": {
                        "name": "maxmemory-policy",
                        "value": "volatile-lru",
                        "data_type": "string",
                        "modifiable": True,
                        "description": "Max memory policy",
                        "allowed_values": "allkeys-lru,volatile-lru,allkeys-random,volatile-random,volatile-ttl,noeviction",
                    },
                },
            },
        }


class EventSubscriptionRequest(BaseModel):
    """Request model for creating an event subscription."""

    subscription_name: str = Field(...,
                                   description="The name of the event subscription")
    sns_topic_arn: str = Field(...,
                               description="The ARN of the SNS topic to notify")
    source_type: Literal["cache-cluster", "cache-parameter-group", "cache-security-group",
                         "cache-subnet-group"] = Field(..., description="The type of source")
    source_ids: Optional[List[str]] = Field(
        None, description="List of source IDs to monitor")
    event_categories: Optional[List[str]] = Field(
        None, description="Event categories to subscribe to")
    enabled: bool = Field(
        True, description="Whether the subscription is enabled")
    tags: Dict[str, str] = Field(
        default_factory=dict, description="Resource tags")


class EventSubscriptionStatus(BaseModel):
    """Status information for an event subscription."""

    subscription_name: str = Field(...,
                                   description="The name of the event subscription")
    sns_topic_arn: str = Field(..., description="The ARN of the SNS topic")
    source_type: str = Field(...,
                             description="The type of source being monitored")
    source_ids: List[str] = Field(
        default_factory=list, description="List of source IDs being monitored")
    event_categories: List[str] = Field(
        default_factory=list, description="Event categories being monitored")
    enabled: bool = Field(...,
                          description="Whether the subscription is enabled")
    status: str = Field(..., description="The status of the subscription")


class MetricRequest(BaseModel):
    """Request model for retrieving performance metrics."""

    metric_name: str = Field(...,
                             description="The name of the metric to retrieve")
    cluster_id: str = Field(..., description="The ID of the cluster")
    period: int = Field(
        60, description="The granularity, in seconds, of the returned datapoints")
    start_time: datetime = Field(...,
                                 description="The start time of the metric data")
    end_time: datetime = Field(...,
                               description="The end time of the metric data")
    statistics: List[Literal["Average", "Maximum", "Minimum", "Sum", "SampleCount"]] = Field(
        default=["Average"], description="The metric statistics to return"
    )


class MetricDatapoint(BaseModel):
    """A single metric datapoint."""

    timestamp: datetime = Field(...,
                                description="The timestamp of the datapoint")
    value: float = Field(..., description="The value of the metric")
    unit: str = Field(..., description="The unit of the metric")


class MetricResponse(BaseModel):
    """Response model for performance metrics."""

    metric_name: str = Field(..., description="The name of the metric")
    namespace: str = Field(
        "AWS/ElastiCache", description="The metric namespace")
    datapoints: List[MetricDatapoint] = Field(
        default_factory=list, description="The metric datapoints")


class ReplicationGroupRequest(BaseModel):
    """Request model for creating a replication group."""

    group_id: str = Field(..., description="The ID of the replication group")
    description: str = Field(...,
                             description="Description of the replication group")
    node_type: NodeType = Field(..., description="The node type for the group")
    engine_version: str = Field(..., description="Redis engine version")
    num_node_groups: int = Field(
        1, description="Number of node groups (shards)", ge=1)
    replicas_per_node_group: int = Field(
        1, description="Number of replica nodes per shard", ge=0)
    automatic_failover: bool = Field(
        True, description="Enable automatic failover")
    multi_az: bool = Field(True, description="Enable Multi-AZ")
    subnet_group: Optional[SubnetGroup] = Field(
        None, description="Subnet group for the replication group")
    security_groups: Optional[List[SecurityGroup]] = Field(
        None, description="Security groups")
    parameter_group: Optional[str] = Field(
        None, description="Parameter group name")
    port: int = Field(6379, description="Port number")
    maintenance_window: Optional[str] = Field(
        None, description="Preferred maintenance window")
    tags: Dict[str, str] = Field(
        default_factory=dict, description="Resource tags")


class ReplicationGroupStatus(BaseModel):
    """Status information for a replication group."""

    group_id: str = Field(..., description="The ID of the replication group")
    status: str = Field(..., description="The status of the replication group")
    description: str = Field(...,
                             description="Description of the replication group")
    node_groups: List[Dict[str, Any]] = Field(
        default_factory=list, description="Node group information")
    automatic_failover: str = Field(...,
                                    description="Automatic failover status")
    multi_az: bool = Field(..., description="Multi-AZ status")
    endpoint: Optional[str] = Field(
        None, description="Primary endpoint address")
    port: Optional[int] = Field(None, description="Port number")


class MaintenanceWindow(BaseModel):
    """Maintenance window configuration."""

    day_of_week: Literal["sun", "mon", "tue", "wed", "thu", "fri", "sat"] = Field(
        ..., description="Day of the week"
    )
    start_time: str = Field(..., description="Start time in UTC (HH:mm)")
    duration: int = Field(..., description="Duration in hours", ge=1, le=24)


class ModifyMaintenanceWindowRequest(BaseModel):
    """Request model for modifying maintenance window."""

    cluster_id: str = Field(..., description="The ID of the cluster")
    window: MaintenanceWindow = Field(...,
                                      description="New maintenance window configuration")


@dataclass
class ServerlessScalingConfiguration:
    """Configuration for ElastiCache Serverless scaling."""
    minimum_capacity: float  # ECU units (0.5 to 100)
    maximum_capacity: float  # ECU units (0.5 to 100)


@dataclass
class CreateServerlessRequest:
    """Request to create a serverless cache."""
    cache_name: str
    description: Optional[str] = None
    major_engine_version: str = "7.0"  # Redis version
    daily_backup_window: Optional[str] = None  # Format: "04:00-05:00"
    backup_retention_period: Optional[int] = None  # 0-35 days
    security_group_ids: Optional[List[str]] = None
    subnet_ids: Optional[List[str]] = None
    kms_key_id: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    scaling: Optional[ServerlessScalingConfiguration] = None


@dataclass
class ServerlessStatus:
    """Status of a serverless cache."""
    cache_name: str
    status: str  # available, creating, modifying, deleting
    endpoint: Optional[str] = None
    reader_endpoint: Optional[str] = None
    major_engine_version: str = "7.0"
    daily_backup_window: Optional[str] = None
    backup_retention_period: Optional[int] = None
    security_group_ids: Optional[List[str]] = None
    subnet_ids: Optional[List[str]] = None
    kms_key_id: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    scaling: Optional[ServerlessScalingConfiguration] = None


@dataclass
class ModifyServerlessRequest:
    """Request to modify a serverless cache."""
    cache_name: str
    description: Optional[str] = None
    daily_backup_window: Optional[str] = None
    backup_retention_period: Optional[int] = None
    security_group_ids: Optional[List[str]] = None
    scaling: Optional[ServerlessScalingConfiguration] = None
    tags: Optional[Dict[str, str]] = None

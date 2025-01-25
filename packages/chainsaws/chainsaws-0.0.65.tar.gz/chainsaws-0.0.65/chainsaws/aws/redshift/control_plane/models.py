"""Unified models for Redshift Control Plane operations."""

from datetime import datetime
from typing import Dict, List, Optional, Final
from pydantic import BaseModel, Field


# Constants
UNLIMITED_CONNECTIONS: Final[int] = -1


# Cluster related models
class NodeType(BaseModel):
    """Redshift node type configuration."""

    name: str = Field(...,
                      description="Node type identifier (e.g., dc2.large)")
    vcpu: int = Field(..., description="Number of virtual CPUs")
    memory_gb: int = Field(..., description="Memory in GB")
    storage_gb: int = Field(..., description="Storage capacity in GB")

    class Config:
        frozen = True


class NetworkConfig(BaseModel):
    """Network configuration for Redshift cluster."""

    vpc_id: str = Field(..., description="VPC ID")
    subnet_ids: List[str] = Field(..., description="List of subnet IDs")
    security_group_ids: List[str] = Field(...,
                                          description="List of security group IDs")
    publicly_accessible: bool = Field(
        default=False,
        description="Whether cluster is publicly accessible"
    )


class MaintenanceWindow(BaseModel):
    """Maintenance window configuration."""

    day_of_week: int = Field(..., description="Day of week (0-6)", ge=0, le=6)
    start_time: str = Field(..., description="Start time in UTC (HH:mm)")
    duration_hours: int = Field(...,
                                description="Duration in hours", ge=1, le=24)


class BackupConfig(BaseModel):
    """Backup configuration for Redshift cluster."""

    retention_period_days: int = Field(
        default=7,
        description="Backup retention period in days",
        ge=1
    )
    automated_snapshot_start_time: str = Field(
        ...,
        description="Daily time when automated snapshots are taken (UTC HH:mm)"
    )


class ClusterConfig(BaseModel):
    """Configuration for creating/modifying a Redshift cluster."""

    cluster_identifier: str = Field(...,
                                    description="Unique cluster identifier")
    node_type: str = Field(..., description="Node type (e.g., dc2.large)")
    number_of_nodes: int = Field(
        default=1,
        description="Number of compute nodes",
        ge=1
    )
    master_username: str = Field(..., description="Master user name")
    master_user_password: str = Field(..., description="Master user password")
    database_name: str = Field(..., description="Initial database name")
    port: int = Field(default=5439, description="Database port")
    network: NetworkConfig = Field(..., description="Network configuration")
    maintenance_window: Optional[MaintenanceWindow] = Field(
        None,
        description="Maintenance window configuration"
    )
    backup: Optional[BackupConfig] = Field(
        None,
        description="Backup configuration"
    )
    encrypted: bool = Field(
        default=True,
        description="Whether to encrypt the cluster"
    )
    kms_key_id: Optional[str] = Field(
        None,
        description="KMS key ID for encryption"
    )
    tags: dict = Field(default_factory=dict, description="Resource tags")


class ClusterStatus(BaseModel):
    """Current status of a Redshift cluster."""

    cluster_identifier: str = Field(..., description="Cluster identifier")
    status: str = Field(..., description="Current cluster status")
    node_type: str = Field(..., description="Node type")
    number_of_nodes: int = Field(..., description="Number of nodes")
    availability_zone: str = Field(..., description="Availability zone")
    vpc_id: str = Field(..., description="VPC ID")
    publicly_accessible: bool = Field(..., description="Publicly accessible")
    encrypted: bool = Field(..., description="Encrypted status")
    database_name: str = Field(..., description="Database name")
    master_username: str = Field(..., description="Master username")
    endpoint_address: Optional[str] = Field(
        None, description="Endpoint address")
    endpoint_port: Optional[int] = Field(None, description="Endpoint port")
    cluster_create_time: Optional[datetime] = Field(
        None,
        description="Cluster creation time"
    )
    automated_snapshot_retention_period: int = Field(
        ...,
        description="Backup retention period"
    )
    cluster_security_groups: List[str] = Field(
        ...,
        description="Security group IDs"
    )
    vpc_security_groups: List[str] = Field(
        ...,
        description="VPC security group IDs"
    )
    pending_modified_values: dict = Field(
        default_factory=dict,
        description="Pending changes"
    )
    preferred_maintenance_window: str = Field(
        ...,
        description="Maintenance window"
    )
    node_type_parameters: dict = Field(
        default_factory=dict,
        description="Node type specific parameters"
    )
    cluster_version: str = Field(..., description="Redshift engine version")
    allow_version_upgrade: bool = Field(...,
                                        description="Allow version upgrade")
    number_of_nodes_ready: Optional[int] = Field(
        None,
        description="Number of nodes ready"
    )
    total_storage_capacity_in_mega_bytes: int = Field(
        ...,
        description="Total storage capacity"
    )
    aqua_configuration_status: str = Field(
        ...,
        description="AQUA configuration status"
    )
    default_iam_role_arn: Optional[str] = Field(
        None,
        description="Default IAM role ARN"
    )
    maintenance_track_name: str = Field(..., description="Maintenance track")
    elastic_resize_number_of_node_options: Optional[str] = Field(
        None,
        description="Available node count options for elastic resize"
    )
    deferred_maintenance_windows: List[dict] = Field(
        default_factory=list,
        description="Deferred maintenance windows"
    )
    snapshot_schedule_state: str = Field(
        ...,
        description="Snapshot schedule state"
    )
    expected_next_snapshot_schedule_time: Optional[datetime] = Field(
        None,
        description="Next scheduled snapshot time"
    )
    expected_next_snapshot_schedule_time_status: str = Field(
        ...,
        description="Next snapshot schedule status"
    )
    next_maintenance_window_start_time: Optional[datetime] = Field(
        None,
        description="Next maintenance window start"
    )


# Security related models
class IamRole(BaseModel):
    """IAM role configuration."""

    role_arn: str = Field(..., description="IAM role ARN")
    feature_name: Optional[str] = Field(
        None,
        description="Feature name this role is associated with"
    )


class SecurityGroup(BaseModel):
    """Security group configuration."""

    group_id: str = Field(..., description="Security group ID")
    group_name: str = Field(..., description="Security group name")
    vpc_id: str = Field(..., description="VPC ID")
    description: str = Field(..., description="Security group description")
    tags: dict = Field(default_factory=dict, description="Resource tags")


class InboundRule(BaseModel):
    """Inbound rule for security group."""

    protocol: str = Field(..., description="Protocol (tcp, udp, icmp)")
    from_port: int = Field(..., description="Start port")
    to_port: int = Field(..., description="End port")
    cidr_blocks: List[str] = Field(
        default_factory=list,
        description="CIDR blocks"
    )
    security_group_ids: List[str] = Field(
        default_factory=list,
        description="Security group IDs"
    )
    description: Optional[str] = Field(None, description="Rule description")


class SecurityGroupConfig(BaseModel):
    """Configuration for creating/modifying a security group."""

    group_name: str = Field(..., description="Security group name")
    description: str = Field(..., description="Security group description")
    vpc_id: str = Field(..., description="VPC ID")
    inbound_rules: List[InboundRule] = Field(
        default_factory=list,
        description="Inbound rules"
    )
    tags: dict = Field(default_factory=dict, description="Resource tags")


class User(BaseModel):
    """Redshift database user."""

    username: str = Field(..., description="User name")
    password: Optional[str] = Field(None, description="User password")
    connection_limit: int = Field(
        default=UNLIMITED_CONNECTIONS,
        description="Maximum number of connections"
    )
    valid_until: Optional[str] = Field(
        None,
        description="Password validity period"
    )
    create_database: bool = Field(
        default=False,
        description="Permission to create databases"
    )
    superuser: bool = Field(
        default=False,
        description="Superuser status"
    )


class Group(BaseModel):
    """Redshift user group."""

    group_name: str = Field(..., description="Group name")
    users: List[str] = Field(default_factory=list, description="Group members")


class Permission(BaseModel):
    """Database object permission."""

    database: str = Field(..., description="Database name")
    schema: Optional[str] = Field(None, description="Schema name")
    table: Optional[str] = Field(None, description="Table name")
    permissions: List[str] = Field(..., description="Granted permissions")


class GrantConfig(BaseModel):
    """Configuration for granting permissions."""

    grantee: str = Field(..., description="User or group name")
    grantee_type: str = Field(..., description="USER or GROUP")
    permissions: List[Permission] = Field(...,
                                          description="Permissions to grant")


# Parameter related models
class ParameterValue(BaseModel):
    """Parameter value with metadata."""

    name: str = Field(..., description="Parameter name")
    value: str = Field(..., description="Parameter value")
    description: str = Field(..., description="Parameter description")
    source: str = Field(..., description="Value source")
    data_type: str = Field(..., description="Parameter data type")
    allowed_values: str = Field(..., description="Allowed values")
    apply_type: str = Field(..., description="static or dynamic")
    is_modifiable: bool = Field(...,
                                description="Whether parameter can be modified")
    minimum_engine_version: str = Field(
        ...,
        description="Minimum engine version required"
    )


class ParameterGroupFamily(BaseModel):
    """Redshift parameter group family."""

    name: str = Field(..., description="Family name")
    description: str = Field(..., description="Family description")
    engine: str = Field(..., description="Database engine")
    engine_version: str = Field(..., description="Engine version")


class ParameterGroupConfig(BaseModel):
    """Configuration for parameter group."""

    name: str = Field(..., description="Parameter group name")
    family: str = Field(..., description="Parameter group family")
    description: str = Field(..., description="Parameter group description")
    parameters: Dict[str, str] = Field(
        default_factory=dict,
        description="Parameter name-value pairs"
    )
    tags: Dict[str, str] = Field(
        default_factory=dict,
        description="Resource tags"
    )


class ParameterGroupStatus(BaseModel):
    """Status of a parameter group."""

    name: str = Field(..., description="Parameter group name")
    family: str = Field(..., description="Parameter group family")
    description: str = Field(..., description="Parameter group description")
    parameters: Dict[str, ParameterValue] = Field(
        ...,
        description="Parameter details"
    )
    tags: Dict[str, str] = Field(
        default_factory=dict,
        description="Resource tags"
    )


class ParameterModification(BaseModel):
    """Parameter modification details."""

    parameter_name: str = Field(..., description="Parameter name")
    current_value: str = Field(..., description="Current value")
    new_value: str = Field(..., description="New value")
    modification_state: str = Field(
        ...,
        description="pending-reboot, applying, etc."
    )
    modification_time: str = Field(..., description="Modification timestamp")


class ApplyStatus(BaseModel):
    """Status of parameter modifications."""

    parameters_to_apply: List[str] = Field(
        ...,
        description="Parameters pending application"
    )
    parameters_applied: List[str] = Field(
        ...,
        description="Parameters successfully applied"
    )
    parameters_with_errors: Dict[str, str] = Field(
        default_factory=dict,
        description="Parameters that failed to apply with error messages"
    )
    requires_reboot: bool = Field(
        ...,
        description="Whether cluster reboot is required"
    )

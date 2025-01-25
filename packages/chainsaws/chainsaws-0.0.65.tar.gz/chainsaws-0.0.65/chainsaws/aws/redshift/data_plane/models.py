"""Model definitions for Redshift API."""

from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Dict, Generic, List, Literal, Optional, TypeVar, TypedDict, Union
from pydantic import BaseModel, Field

from chainsaws.aws.shared.config import APIConfig


class RedshiftAPIConfig(APIConfig):
    """Configuration for RedshiftAPI."""

    database: str = Field(..., description="Default database name")
    schema: str = Field(default="public", description="Default schema name")
    port: int = Field(default=5439, description="Redshift port")
    max_pool_connections: int = Field(
        default=50,
        description="Maximum number of connections in the pool",
        ge=1,
        le=500
    )
    ssl_mode: str = Field(
        default="verify-full",
        description="SSL mode for connections"
    )
    ssl_cert_path: Optional[str] = Field(
        default=None,
        description="Path to SSL certificate"
    )
    connection_timeout: int = Field(
        default=30,
        description="Connection timeout in seconds",
        ge=1,
        le=300
    )


class ConnectionPoolStatus(BaseModel):
    """Status information about the connection pool."""

    total_connections: int = Field(
        description="Total number of connections in the pool")
    active_connections: int = Field(
        description="Number of currently active connections")
    available_connections: int = Field(
        description="Number of available connections")
    connection_attempts: int = Field(
        description="Number of connection attempts made")
    last_reset: datetime = Field(description="Timestamp of last pool reset")
    max_connections: int = Field(description="Maximum allowed connections")

    class Config:
        json_schema_extra = {
            "example": {
                "total_connections": 50,
                "active_connections": 10,
                "available_connections": 40,
                "connection_attempts": 1,
                "last_reset": "2024-01-01T00:00:00",
                "max_connections": 50
            }
        }


class BatchOperationResult(BaseModel):
    """Result of a batch operation."""

    total_records: int = Field(
        description="Total number of records in the batch")
    processed_records: int = Field(
        description="Number of successfully processed records")
    failed_records: int = Field(description="Number of failed records")
    execution_time: float = Field(
        description="Total execution time in seconds")

    @property
    def success_rate(self) -> float:
        """Calculate the success rate of the batch operation."""
        return self.processed_records / self.total_records if self.total_records > 0 else 0.0

    class Config:
        json_schema_extra = {
            "example": {
                "total_records": 1000,
                "processed_records": 995,
                "failed_records": 5,
                "execution_time": 1.234
            }
        }


class QueryState(str, Enum):
    """State of query execution."""
    SUBMITTED = "SUBMITTED"
    STARTED = "STARTED"
    FINISHED = "FINISHED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"


class QueryStatistics(TypedDict):
    """Statistics about query execution."""
    elapsed_time: float
    cpu_time: float
    queued_time: float
    bytes_scanned: int
    rows_produced: int
    rows_affected: int


class Column(TypedDict):
    """Column information."""
    name: str
    type: str
    nullable: bool
    default: Optional[str]
    encoding: Optional[str]
    distkey: bool
    sortkey: bool
    primary_key: bool


class Table(TypedDict):
    """Table information."""
    schema: str
    name: str
    type: str
    columns: List[Column]
    distribution_style: str
    sort_keys: List[str]
    encoded: bool


class Schema(TypedDict):
    """Schema information."""
    name: str
    owner: str
    tables: List[Table]


class Database(TypedDict):
    """Database information."""
    name: str
    owner: str
    schemas: List[Schema]
    created: datetime
    last_modified: datetime


class ClusterStatus(str, Enum):
    """Redshift cluster status."""
    AVAILABLE = "available"
    CREATING = "creating"
    DELETING = "deleting"
    FINAL_SNAPSHOT = "final-snapshot"
    HARDWARE_FAILURE = "hardware-failure"
    INCOMPATIBLE_HSM = "incompatible-hsm"
    INCOMPATIBLE_NETWORK = "incompatible-network"
    INCOMPATIBLE_PARAMETERS = "incompatible-parameters"
    INCOMPATIBLE_RESTORE = "incompatible-restore"
    MODIFYING = "modifying"
    REBOOTING = "rebooting"
    RENAMING = "renaming"
    RESIZING = "resizing"
    ROTATING_KEYS = "rotating-keys"
    STORAGE_FULL = "storage-full"
    UPDATING_HSM = "updating-hsm"


class ClusterInfo(TypedDict):
    """Redshift cluster information."""
    identifier: str
    status: ClusterStatus
    availability_zone: str
    node_type: str
    cluster_type: str
    number_of_nodes: int
    master_username: str
    database_name: str
    port: int
    cluster_version: str
    vpc_id: Optional[str]
    encrypted: bool
    maintenance_window: str
    automated_snapshot_retention_period: int
    preferred_maintenance_window: str
    availability_zone_relocation_status: str
    cluster_namespace_arn: str
    total_storage_capacity_in_mega_bytes: int
    aqua_configuration_status: str
    default_iam_role_arn: str
    expected_next_snapshot_schedule_time: datetime
    expected_next_snapshot_schedule_time_status: str
    next_maintenance_window_start_time: datetime
    resize_info: Optional[Dict[str, Any]]


class UserInfo(TypedDict):
    """Redshift user information."""
    name: str
    connection_limit: int
    created: datetime
    expires: Optional[datetime]
    system_user: bool
    super_user: bool


class GroupInfo(TypedDict):
    """Redshift group information."""
    name: str
    created: datetime
    users: List[str]


class QueryResult(TypedDict):
    """Complete query execution result."""
    query_id: str
    query: str
    state: QueryState
    statistics: Optional[QueryStatistics]
    result_rows: Optional[List[Dict[str, Any]]]
    error_message: Optional[str]


T = TypeVar('T')


class TypedQueryResult(Generic[T]):
    """Typed query result with metadata."""

    def __init__(
        self,
        data: List[T],
        execution_time: float,
        scanned_bytes: int,
        row_count: int,
        query_id: str,
        completed_at: datetime
    ):
        self.data = data
        self.execution_time = execution_time
        self.scanned_bytes = scanned_bytes
        self.row_count = row_count
        self.query_id = query_id
        self.completed_at = completed_at

    @classmethod
    def from_query_result(cls, result: QueryResult, output_type: type[T]) -> 'TypedQueryResult[T]':
        """Create TypedQueryResult from raw query result."""
        stats = result.get("statistics", {})
        rows = result.get("result_rows", [])

        # Convert raw rows to typed objects
        typed_data = [output_type(**row) for row in rows]

        return cls(
            data=typed_data,
            execution_time=float(stats.get("elapsed_time", 0)),
            scanned_bytes=int(stats.get("bytes_scanned", 0)),
            row_count=len(rows),
            query_id=result["query_id"],
            completed_at=datetime.now()
        )


class QueryPerformanceReport(BaseModel):
    """Query performance analysis report."""

    execution_time: float = Field(
        description="Total execution time in seconds")
    data_scanned: int = Field(description="Amount of data scanned in bytes")
    cost_estimate: float = Field(description="Estimated cost of the query")
    engine_version: str = Field(description="Redshift engine version")
    suggestions: List[str] = Field(description="Optimization suggestions")
    risk_level: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        description="Performance risk level")
    bottlenecks: List[str] = Field(description="Identified bottlenecks")
    optimization_tips: List[str] = Field(description="Tips for optimization")
    partition_info: Optional[Dict[str, Any]] = Field(
        description="Partition-related information")
    join_info: Optional[Dict[str, Any]] = Field(
        description="Join-related information")

    class Config:
        json_schema_extra: ClassVar[dict[str, Any]] = {
            "example": {
                "execution_time": 1.234,
                "data_scanned": 1024000,
                "cost_estimate": 0.05,
                "engine_version": "1.0.34567",
                "suggestions": [
                    "Add a sortkey on column 'timestamp'",
                    "Consider using DISTSTYLE KEY"
                ],
                "risk_level": "MEDIUM",
                "bottlenecks": ["Large broadcast join", "Missing sortkey"],
                "optimization_tips": [
                    "Rewrite join condition",
                    "Add compression encoding"
                ]
            }
        }


class DetailedError(BaseModel):
    """Detailed error information with suggestions."""

    error_code: str = Field(description="Error code")
    message: str = Field(description="Error message")
    details: Dict[str, Any] = Field(description="Additional error details")
    suggestions: List[str] = Field(description="Error resolution suggestions")
    query_stage: str = Field(description="Stage where error occurred")
    error_location: Optional[str] = Field(description="Location of the error")
    error_type: str = Field(default="UNKNOWN", description="Type of error")

    @property
    def is_recoverable(self) -> bool:
        """Check if the error is potentially recoverable."""
        return self.error_type not in ["FATAL", "SYSTEM"]


"""Data models for Redshift operations."""

# Basic value types that can be used in Redshift
RedshiftValue = Union[
    str,
    int,
    float,
    bool,
    datetime,
    None,
    List['RedshiftValue'],
    Dict[str, 'RedshiftValue']
]

# Parameter types for queries
QueryParams = Dict[str, RedshiftValue]

# Record types
RedshiftRecord = Dict[str, RedshiftValue]
RedshiftRecordList = List[RedshiftRecord]


class QueryState(str, Enum):
    """States of query execution."""
    QUEUED = "QUEUED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"


class QueryResult:
    """Result of a query execution."""

    def __init__(
        self,
        query_id: str,
        state: QueryState,
        result_rows: List[RedshiftRecord],
        affected_rows: int,
        statistics: Optional['QueryStatistics'] = None,
        error: Optional['DetailedError'] = None
    ):
        self.query_id = query_id
        self.state = state
        self.result_rows = result_rows
        self.affected_rows = affected_rows
        self.statistics = statistics
        self.error = error


class QueryStatistics:
    """Statistics for query execution."""

    def __init__(
        self,
        execution_time: float,
        cpu_time: float,
        queued_time: float,
        processed_rows: int,
        processed_bytes: int,
        peak_memory_usage: int
    ):
        self.execution_time = execution_time
        self.cpu_time = cpu_time
        self.queued_time = queued_time
        self.processed_rows = processed_rows
        self.processed_bytes = processed_bytes
        self.peak_memory_usage = peak_memory_usage

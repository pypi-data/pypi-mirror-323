from typing import Optional, List, Dict, Literal, Any, TypedDict
from pydantic import BaseModel, Field

from chainsaws.aws.shared.config import APIConfig


class ECSAPIConfig(APIConfig):
    """Configuration for ECS API."""
    max_retries: int = Field(
        3, description="Maximum number of API call retries")
    timeout: int = Field(30, description="Timeout for API calls in seconds")


class CapacityProviderStrategy(BaseModel):
    """ECS capacity provider strategy configuration."""
    capacity_provider: str = Field(...,
                                   description="Name of the capacity provider")
    weight: Optional[int] = Field(
        None, description="Weight value designating relative percentage of the total number of tasks")
    base: Optional[int] = Field(
        None, description="Number of tasks that should use the specified provider")


class DeploymentConfiguration(BaseModel):
    """ECS deployment configuration."""
    maximum_percent: Optional[int] = Field(
        None, description="Upper limit on the number of tasks that can run during a deployment")
    minimum_healthy_percent: Optional[int] = Field(
        None, description="Lower limit on the number of running tasks during a deployment")
    deployment_circuit_breaker: Optional[Dict[str, bool]] = Field(
        None, description="Circuit breaker settings for deployment")
    alarms: Optional[Dict[str, List[str]]] = Field(
        None, description="CloudWatch alarms to monitor during deployment")


class DeploymentController(BaseModel):
    """ECS deployment controller configuration."""
    type: Literal["ECS", "CODE_DEPLOY", "EXTERNAL"] = Field(
        "ECS", description="Type of deployment controller")


class NetworkConfiguration(BaseModel):
    """ECS network configuration."""
    awsvpc_configuration: Optional[Dict[str, Any]] = Field(
        None, description="VPC configuration for the task or service")


class LoadBalancer(BaseModel):
    """ECS load balancer configuration."""
    target_group_arn: Optional[str] = Field(
        None, description="ARN of the target group")
    load_balancer_name: Optional[str] = Field(
        None, description="Name of the load balancer")
    container_name: str = Field(
        ..., description="Name of the container to associate with the load balancer")
    container_port: int = Field(
        ..., description="Port on the container to associate with the load balancer")


class PlacementConstraint(BaseModel):
    """ECS placement constraint configuration."""
    type: Literal["distinctInstance",
                  "memberOf"] = Field(..., description="Type of constraint")
    expression: Optional[str] = Field(
        None, description="Cluster query language expression")


class PlacementStrategy(BaseModel):
    """ECS placement strategy configuration."""
    type: Literal["random", "spread",
                  "binpack"] = Field(..., description="Type of placement strategy")
    field: Optional[str] = Field(
        None, description="Field to apply the placement strategy against")


class ServiceRegistry(BaseModel):
    """ECS service registry configuration."""
    registry_arn: str = Field(..., description="ARN of the service registry")
    port: Optional[int] = Field(
        None, description="Port value used if the service discovery service specified an SRV record")
    container_name: Optional[str] = Field(
        None, description="Container name value already specified in the task definition")
    container_port: Optional[int] = Field(
        None, description="Port value specified in the task definition")


class Tag(BaseModel):
    """AWS resource tag."""
    key: str = Field(..., description="Tag key")
    value: str = Field(..., description="Tag value")


class RuntimePlatform(BaseModel):
    """ECS runtime platform configuration."""
    cpu_architecture: Optional[Literal["X86_64", "ARM64"]] = Field(
        None, description="CPU architecture")
    operating_system_family: Optional[str] = Field(
        None, description="Operating system family")


class EphemeralStorage(BaseModel):
    """ECS ephemeral storage configuration."""
    size_in_gib: int = Field(...,
                             description="Size of the ephemeral storage in GiB")


class InferenceAccelerator(BaseModel):
    """ECS inference accelerator configuration."""
    device_name: str = Field(...,
                             description="Elastic Inference accelerator device name")
    device_type: str = Field(...,
                             description="Elastic Inference accelerator type")


class ProxyConfiguration(BaseModel):
    """ECS proxy configuration."""
    type: Literal["APPMESH"] = Field(..., description="Proxy type")
    container_name: str = Field(
        ..., description="Name of the container that will serve as the App Mesh proxy")
    properties: Optional[List[Dict[str, str]]] = Field(
        None, description="Set of network configuration parameters for the proxy")


class Volume(BaseModel):
    """ECS volume configuration."""
    name: str = Field(..., description="Name of the volume")
    host: Optional[Dict[str, str]] = Field(
        None, description="Host-specific settings")
    docker_volume_configuration: Optional[Dict[str, Any]] = Field(
        None, description="Docker volume configuration")
    efs_volume_configuration: Optional[Dict[str, Any]] = Field(
        None, description="Amazon EFS volume configuration")
    fsx_windows_file_server_volume_configuration: Optional[Dict[str, Any]] = Field(
        None, description="FSx for Windows File Server volume configuration")


class ContainerDefinition(BaseModel):
    """ECS container definition."""
    name: str = Field(..., description="Name of the container")
    image: str = Field(...,
                       description="Docker image to use for the container")
    cpu: Optional[int] = Field(
        None, description="Number of cpu units to reserve for the container")
    memory: Optional[int] = Field(
        None, description="Amount of memory (in MiB) to allow the container to use")
    memory_reservation: Optional[int] = Field(
        None, description="Soft limit (in MiB) of memory to reserve for the container")
    links: Optional[List[str]] = Field(
        None, description="Links to other containers")
    port_mappings: Optional[List[Dict[str, Any]]] = Field(
        None, description="Port mappings for the container")
    essential: bool = Field(
        True, description="Whether the container is essential")
    entry_point: Optional[List[str]] = Field(
        None, description="Entry point that is passed to the container")
    command: Optional[List[str]] = Field(
        None, description="Command that is passed to the container")
    environment: Optional[List[Dict[str, str]]] = Field(
        None, description="Environment variables")
    environment_files: Optional[List[Dict[str, str]]] = Field(
        None, description="List of files containing environment variables")
    mount_points: Optional[List[Dict[str, Any]]] = Field(
        None, description="Mount points for data volumes in your container")
    volumes_from: Optional[List[Dict[str, Any]]] = Field(
        None, description="Data volumes to mount from another container")
    linux_parameters: Optional[Dict[str, Any]] = Field(
        None, description="Linux-specific modifications that are applied to the container")
    secrets: Optional[List[Dict[str, str]]] = Field(
        None, description="Secrets to pass to the container")
    depends_on: Optional[List[Dict[str, str]]] = Field(
        None, description="Container dependencies")
    start_timeout: Optional[int] = Field(
        None, description="Time duration (in seconds) to wait before giving up on resolving dependencies for a container")
    stop_timeout: Optional[int] = Field(
        None, description="Time duration (in seconds) to wait before the container is forcefully killed")
    hostname: Optional[str] = Field(
        None, description="Hostname to use for your container")
    user: Optional[str] = Field(
        None, description="User name or UID to use inside the container")
    working_directory: Optional[str] = Field(
        None, description="Working directory in which to run commands inside the container")
    disable_networking: Optional[bool] = Field(
        None, description="Whether networking is disabled within the container")
    privileged: Optional[bool] = Field(
        None, description="Whether the container is given elevated privileges")
    readonly_root_filesystem: Optional[bool] = Field(
        None, description="Whether the container is given read-only access to its root file system")
    dns_servers: Optional[List[str]] = Field(
        None, description="DNS servers that are presented to the container")
    dns_search_domains: Optional[List[str]] = Field(
        None, description="DNS search domains that are presented to the container")
    extra_hosts: Optional[List[Dict[str, str]]] = Field(
        None, description="Hostname and IP address entries to add to the container's /etc/hosts file")
    docker_security_options: Optional[List[str]] = Field(
        None, description="Custom labels to apply to the container's SELinux security options")
    interactive: Optional[bool] = Field(
        None, description="Whether this container is allocated a TTY")
    pseudo_terminal: Optional[bool] = Field(
        None, description="Whether a TTY should be allocated")
    docker_labels: Optional[Dict[str, str]] = Field(
        None, description="Docker labels")
    ulimits: Optional[List[Dict[str, Any]]] = Field(
        None, description="List of ulimits to set in the container")
    log_configuration: Optional[Dict[str, Any]] = Field(
        None, description="Log configuration options to send to the container")
    health_check: Optional[Dict[str, Any]] = Field(
        None, description="Container health check command and associated configuration parameters")
    system_controls: Optional[List[Dict[str, str]]] = Field(
        None, description="List of namespaced kernel parameters to set in the container")
    resource_requirements: Optional[List[Dict[str, str]]] = Field(
        None, description="Type and amount of a resource to assign to a container")
    firelens_configuration: Optional[Dict[str, str]] = Field(
        None, description="FireLens configuration for the container")
    repository_credentials: Optional[Dict[str, str]] = Field(
        None, description="Private repository authentication credentials")


class LogConfiguration(BaseModel):
    """Log configuration for execute command."""
    cloud_watch_log_group_name: Optional[str] = Field(
        None, description="The name of the CloudWatch log group to send logs to")
    cloud_watch_encryption_enabled: Optional[bool] = Field(
        None, description="Whether to use encryption on the CloudWatch logs")
    s3_bucket_name: Optional[str] = Field(
        None, description="The name of the S3 bucket to send logs to")
    s3_encryption_enabled: Optional[bool] = Field(
        None, description="Whether to use encryption on the S3 logs")
    s3_key_prefix: Optional[str] = Field(
        None, description="Optional folder in the S3 bucket to place logs in")


class ExecuteCommandConfiguration(BaseModel):
    """Execute command configuration for the cluster."""
    kms_key_id: Optional[str] = Field(
        None, description="KMS key ID to encrypt the data between the local client and the container")
    logging: Optional[Literal["NONE", "DEFAULT", "OVERRIDE"]] = Field(
        None, description="Log setting for execute command results")
    log_configuration: Optional[LogConfiguration] = Field(
        None, description="Log configuration for execute command results")


class ManagedStorageConfiguration(BaseModel):
    """Managed storage configuration for the cluster."""
    kms_key_id: Optional[str] = Field(
        None, description="KMS key ID to encrypt the managed storage")
    fargate_ephemeral_storage_kms_key_id: Optional[str] = Field(
        None, description="KMS key ID for the Fargate ephemeral storage")


class ClusterSetting(BaseModel):
    """ECS cluster setting for Container Insights."""
    name: Literal["containerInsights"] = Field(
        "containerInsights",
        description="The name of the cluster setting. Must be 'containerInsights'"
    )
    value: Literal["enhanced", "enabled", "disabled"] = Field(
        ...,
        description="The value for Container Insights: 'enhanced' for enhanced observability, 'enabled' for standard Container Insights, 'disabled' to turn off"
    )


class ClusterConfiguration(BaseModel):
    """ECS cluster configuration."""
    cluster_name: str = Field(
        ...,
        description="Name of the cluster. Up to 255 letters (uppercase and lowercase), numbers, underscores, and hyphens are allowed"
    )
    tags: Optional[List[Tag]] = Field(
        None,
        description="Metadata tags for the cluster. Maximum 50 tags, each tag key must be unique"
    )
    settings: Optional[List[ClusterSetting]] = Field(
        None,
        description="Settings for CloudWatch Container Insights. If specified, overrides the containerInsights account setting"
    )
    configuration: Optional[Dict[str, Any]] = Field(
        None,
        description="Execute command and managed storage configuration for the cluster"
    )
    capacity_providers: Optional[List[str]] = Field(
        None,
        description="Short names of capacity providers to associate with the cluster"
    )
    default_capacity_provider_strategy: Optional[List[CapacityProviderStrategy]] = Field(
        None,
        description="Default capacity provider strategy for the cluster"
    )
    service_connect_defaults: Optional[Dict[str, str]] = Field(
        None,
        description="Default Service Connect namespace configuration"
    )

    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "cluster_name": "my-ecs-cluster",
                "tags": [{"key": "Environment", "value": "Production"}],
                "settings": [{
                    "name": "containerInsights",
                    "value": "enhanced"  # or "enabled" or "disabled"
                }],
                "configuration": {
                    "executeCommandConfiguration": {
                        "kmsKeyId": "arn:aws:kms:region:account:key/key-id",
                        "logging": "DEFAULT",
                        "logConfiguration": {
                            "cloudWatchLogGroupName": "/ecs/cluster/exec-logs",
                            "cloudWatchEncryptionEnabled": True
                        }
                    }
                },
                "capacity_providers": ["FARGATE", "FARGATE_SPOT"],
                "default_capacity_provider_strategy": [
                    {
                        "capacityProvider": "FARGATE",
                        "weight": 1,
                        "base": 1
                    }
                ],
                "service_connect_defaults": {
                    "namespace": "my-service-namespace"
                }
            }
        }


class ServiceConfiguration(BaseModel):
    """ECS service configuration."""
    cluster_name: str = Field(..., description="Name of the cluster")
    service_name: str = Field(..., description="Name of the service")
    task_definition: str = Field(
        ..., description="Family and revision or full ARN of the task definition")
    desired_count: int = Field(
        ..., description="Number of instantiations of the task to place and keep running")
    capacity_provider_strategy: Optional[List[CapacityProviderStrategy]] = Field(
        None, description="Capacity provider strategy to use for the service")
    deployment_configuration: Optional[DeploymentConfiguration] = Field(
        None, description="Deployment parameters that control how many tasks run during deployment")
    deployment_controller: Optional[DeploymentController] = Field(
        None, description="Deployment controller to use for the service")
    enable_ecs_managed_tags: Optional[bool] = Field(
        None, description="Whether to enable Amazon ECS managed tags")
    enable_execute_command: Optional[bool] = Field(
        None, description="Whether to enable running commands against containers")
    health_check_grace_period_seconds: Optional[int] = Field(
        None, description="Period of time to ignore failing load balancer health checks")
    launch_type: Optional[Literal["EC2", "FARGATE", "EXTERNAL"]] = Field(
        None, description="Launch type on which to run your service")
    load_balancers: Optional[List[LoadBalancer]] = Field(
        None, description="Load balancers to associate with the service")
    network_configuration: Optional[NetworkConfiguration] = Field(
        None, description="Network configuration for the service")
    placement_constraints: Optional[List[PlacementConstraint]] = Field(
        None, description="Placement constraints for task placement")
    placement_strategy: Optional[List[PlacementStrategy]] = Field(
        None, description="Placement strategies for task placement")
    platform_version: Optional[str] = Field(
        None, description="Platform version on which to run your service")
    propagate_tags: Optional[Literal["SERVICE", "TASK_DEFINITION"]] = Field(
        None, description="Whether to propagate tags from the task definition or service")
    scheduling_strategy: Optional[Literal["REPLICA", "DAEMON"]] = Field(
        None, description="Scheduling strategy to use for the service")
    service_registries: Optional[List[ServiceRegistry]] = Field(
        None, description="Details of the service discovery registries to assign to this service")
    tags: Optional[List[Tag]] = Field(
        None, description="List of tags to associate with the service")


class TaskConfiguration(BaseModel):
    """ECS task configuration."""
    cluster_name: str = Field(..., description="Name of the cluster")
    task_definition: str = Field(
        ..., description="Family and revision or full ARN of the task definition")
    capacity_provider_strategy: Optional[List[CapacityProviderStrategy]] = Field(
        None, description="Capacity provider strategy to use for the task")
    count: int = Field(1, description="Number of tasks to launch")
    enable_ecs_managed_tags: Optional[bool] = Field(
        None, description="Whether to enable Amazon ECS managed tags")
    enable_execute_command: Optional[bool] = Field(
        None, description="Whether to enable running commands against containers")
    group: Optional[str] = Field(
        None, description="Task group to associate with the task")
    launch_type: Optional[Literal["EC2", "FARGATE", "EXTERNAL"]] = Field(
        None, description="Launch type on which to run your task")
    network_configuration: Optional[NetworkConfiguration] = Field(
        None, description="Network configuration for the task")
    overrides: Optional[Dict[str, Any]] = Field(
        None, description="Container overrides to apply to the task")
    placement_constraints: Optional[List[PlacementConstraint]] = Field(
        None, description="Placement constraints for task placement")
    placement_strategy: Optional[List[PlacementStrategy]] = Field(
        None, description="Placement strategies for task placement")
    platform_version: Optional[str] = Field(
        None, description="Platform version on which to run your task")
    propagate_tags: Optional[Literal["TASK_DEFINITION"]] = Field(
        None, description="Whether to propagate tags from the task definition")
    reference_id: Optional[str] = Field(
        None, description="Reference ID to use for the task")
    started_by: Optional[str] = Field(
        None, description="Optional tag specified when a task is started")
    tags: Optional[List[Tag]] = Field(
        None, description="List of tags to associate with the task")


class TaskDefinitionConfiguration(BaseModel):
    """ECS task definition configuration."""
    family: str = Field(..., description="Name of the task definition family")
    container_definitions: List[ContainerDefinition] = Field(
        ..., description="List of container definitions")
    cpu: Optional[str] = Field(
        None, description="Number of CPU units used by the task")
    ephemeral_storage: Optional[EphemeralStorage] = Field(
        None, description="Ephemeral storage settings for the task")
    execution_role_arn: Optional[str] = Field(
        None, description="ARN of the task execution role")
    inference_accelerators: Optional[List[InferenceAccelerator]] = Field(
        None, description="Elastic Inference accelerators to use for the containers")
    ipc_mode: Optional[Literal["host", "task", "none"]] = Field(
        None, description="IPC resource namespace to use")
    memory: Optional[str] = Field(
        None, description="Amount of memory (in MiB) used by the task")
    network_mode: Optional[Literal["bridge", "host", "awsvpc", "none"]] = Field(
        None, description="Docker networking mode to use")
    pid_mode: Optional[Literal["host", "task"]] = Field(
        None, description="Process namespace to use")
    placement_constraints: Optional[List[PlacementConstraint]] = Field(
        None, description="Placement constraints for task placement")
    proxy_configuration: Optional[ProxyConfiguration] = Field(
        None, description="Configuration details for an App Mesh proxy")
    requires_compatibilities: Optional[List[Literal["EC2", "FARGATE"]]] = Field(
        None, description="Launch types required by the task")
    runtime_platform: Optional[RuntimePlatform] = Field(
        None, description="Runtime platform for the task")
    tags: Optional[List[Tag]] = Field(
        None, description="List of tags to associate with the task definition")
    task_role_arn: Optional[str] = Field(
        None, description="ARN of the IAM role that allows containers to make calls to AWS services")
    volumes: Optional[List[Volume]] = Field(
        None, description="List of volume definitions")


class ClusterLogConfiguration(TypedDict, total=False):
    """Log configuration for execute command in cluster response."""
    cloudWatchLogGroupName: str
    cloudWatchEncryptionEnabled: bool
    s3BucketName: str
    s3EncryptionEnabled: bool
    s3KeyPrefix: str


class ExecuteCommandConfigurationResponse(TypedDict, total=False):
    """Execute command configuration in cluster response."""
    kmsKeyId: str
    logging: Literal["NONE", "DEFAULT", "OVERRIDE"]
    logConfiguration: ClusterLogConfiguration


class ManagedStorageConfigurationResponse(TypedDict, total=False):
    """Managed storage configuration in cluster response."""
    kmsKeyId: str
    fargateEphemeralStorageKmsKeyId: str


class ClusterConfigurationResponse(TypedDict, total=False):
    """Configuration in cluster response."""
    executeCommandConfiguration: ExecuteCommandConfigurationResponse
    managedStorageConfiguration: ManagedStorageConfigurationResponse


class ClusterStatistic(TypedDict):
    """Statistic in cluster response."""
    name: str
    value: str


class ClusterTag(TypedDict):
    """Tag in cluster response."""
    key: str
    value: str


class ClusterSetting(TypedDict):
    """Setting in cluster response."""
    name: Literal["containerInsights"]
    value: str


class CapacityProviderStrategy(TypedDict, total=False):
    """Capacity provider strategy in cluster response."""
    capacityProvider: str
    weight: int
    base: int


class AttachmentDetail(TypedDict):
    """Attachment detail in cluster response."""
    name: str
    value: str


class ClusterAttachment(TypedDict):
    """Attachment in cluster response."""
    id: str
    type: str
    status: str
    details: List[AttachmentDetail]


class ServiceConnectDefaults(TypedDict):
    """Service connect defaults in cluster response."""
    namespace: str


class Cluster(TypedDict, total=False):
    """Cluster details in response."""
    clusterArn: str
    clusterName: str
    configuration: ClusterConfigurationResponse
    status: str
    registeredContainerInstancesCount: int
    runningTasksCount: int
    pendingTasksCount: int
    activeServicesCount: int
    statistics: List[ClusterStatistic]
    tags: List[ClusterTag]
    settings: List[ClusterSetting]
    capacityProviders: List[str]
    defaultCapacityProviderStrategy: List[CapacityProviderStrategy]
    attachments: List[ClusterAttachment]
    attachmentsStatus: str
    serviceConnectDefaults: ServiceConnectDefaults


class CreateClusterResponse(TypedDict):
    """Response from create_cluster API call."""
    cluster: Cluster

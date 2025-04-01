from dataclasses import dataclass
from typing import Optional


@dataclass
class InventoryConfig:
    """Configuration for Inventory collection."""

    instance_id: str  # Instance ID
    type_name: str  # Inventory type
    schema_version: str  # Schema version
    capture_time: str  # Data capture time
    content: dict  # Inventory content


@dataclass
class MaintenanceWindowConfig:
    """Configuration for Maintenance Window."""

    name: str  # Window name
    schedule: str  # CRON/Rate expression
    duration: int  # Window duration in hours
    cutoff: int  # Cutoff time in hours
    allow_unregistered_targets: bool = False  # Allow unregistered targets
    tags: Optional[dict[str, str]] = None  # Resource tags

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.name:
            raise ValueError("name is required")
        if not self.schedule:
            raise ValueError("schedule is required")
        if not 1 <= self.duration <= 24:
            raise ValueError("duration must be between 1 and 24 hours")
        if not 0 <= self.cutoff <= self.duration:
            raise ValueError("cutoff must be between 0 and duration")


@dataclass
class MaintenanceWindow:
    """Maintenance Window details."""

    window_id: str  # Window ID
    name: str  # Window name
    status: str  # Window status
    enabled: bool  # Window enabled state
    schedule: str  # Schedule expression
    duration: int  # Duration in hours
    cutoff: int  # Cutoff in hours
    next_execution_time: Optional[str] = None  # Next execution time

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.window_id:
            raise ValueError("window_id is required")
        if not self.name:
            raise ValueError("name is required")
        if not self.schedule:
            raise ValueError("schedule is required")
        if not 1 <= self.duration <= 24:
            raise ValueError("duration must be between 1 and 24 hours")
        if not 0 <= self.cutoff <= self.duration:
            raise ValueError("cutoff must be between 0 and duration")

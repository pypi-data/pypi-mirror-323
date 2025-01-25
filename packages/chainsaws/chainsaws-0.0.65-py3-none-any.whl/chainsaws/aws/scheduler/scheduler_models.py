from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field
from pydantic_core import PydanticCustomError
import re
from croniter import croniter

from chainsaws.aws.lambda_client import LambdaAPIConfig


class ScheduleState(str, Enum):
    """Schedule state enum."""

    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class TimeUnit(str, Enum):
    """Time unit for rate expressions."""

    MINUTE = "minute"
    MINUTES = "minutes"
    HOUR = "hour"
    HOURS = "hours"
    DAY = "day"
    DAYS = "days"


class ScheduleExpression(str):
    """Custom type for schedule expressions with validation."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Any, info: Any) -> "ScheduleExpression":
        if not isinstance(value, str):
            raise PydanticCustomError(
                "string_type",
                "Schedule expression must be a string"
            )

        # at 표현식 검증 (at(yyyy-mm-ddThh:mm:ss))
        at_pattern = r"^at\(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\)$"
        if re.match(at_pattern, value):
            try:
                time_str = value[3:-1]  # 'at(' 와 ')' 제거
                datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
                return cls(value)
            except ValueError as e:
                raise PydanticCustomError(
                    "at_format",
                    "Invalid at expression format: {error}",
                    {"error": str(e)}
                )

        # rate 표현식 검증 (rate(value unit))
        rate_pattern = r"^rate\((\d+) (minute|minutes|hour|hours|day|days)\)$"
        if re.match(rate_pattern, value):
            return cls(value)

        # cron 표현식 검증 (cron(* * * * * *))
        if value.startswith("cron(") and value.endswith(")"):
            cron_expr = value[5:-1]  # 'cron(' 와 ')' 제거
            try:
                croniter(cron_expr)
                return cls(value)
            except ValueError as e:
                raise PydanticCustomError(
                    "cron_format",
                    "Invalid cron expression: {error}",
                    {"error": str(e)}
                )

        raise PydanticCustomError(
            "schedule_format",
            "Invalid schedule expression. Must be one of:\n"
            "- at(yyyy-mm-ddThh:mm:ss)\n"
            "- rate(value unit)\n"
            "- cron(* * * * * *)"
        )


class ScheduleExpressionBuilder:
    """Builder for creating valid schedule expressions."""

    @staticmethod
    def at(time: Union[str, datetime]) -> ScheduleExpression:
        """Create an at expression.

        Args:
            time: Time to schedule at. Can be a datetime object or ISO format string.

        Returns:
            ScheduleExpression: Valid at expression

        Example:
            ```python
            # Using datetime
            expr1 = ScheduleExpressionBuilder.at(datetime(2024, 3, 15, 14, 30))
            # Using string
            expr2 = ScheduleExpressionBuilder.at("2024-03-15T14:30:00")
            ```
        """
        if isinstance(time, datetime):
            time_str = time.strftime("%Y-%m-%dT%H:%M:%S")
        else:
            time_str = time
        return ScheduleExpression(f"at({time_str})")

    @staticmethod
    def rate(value: int, unit: Union[TimeUnit, str]) -> ScheduleExpression:
        """Create a rate expression.

        Args:
            value: Number of time units
            unit: Time unit (minute/minutes/hour/hours/day/days)

        Returns:
            ScheduleExpression: Valid rate expression

        Example:
            ```python
            expr1 = ScheduleExpressionBuilder.rate(5, TimeUnit.MINUTES)
            expr2 = ScheduleExpressionBuilder.rate(1, "day")
            ```
        """
        if isinstance(unit, str):
            unit = TimeUnit(unit)
        return ScheduleExpression(f"rate({value} {unit.value})")

    @staticmethod
    def cron(
        minute: str = "*",
        hour: str = "*",
        day_of_month: str = "*",
        month: str = "*",
        day_of_week: str = "*",
        year: str = "*",
    ) -> ScheduleExpression:
        """Create a cron expression.

        Args:
            minute: Minute field (0-59)
            hour: Hour field (0-23)
            day_of_month: Day of month field (1-31)
            month: Month field (1-12 or JAN-DEC)
            day_of_week: Day of week field (0-6 or SUN-SAT)
            year: Year field

        Returns:
            ScheduleExpression: Valid cron expression

        Example:
            ```python
            # Every day at 8:00 AM UTC
            expr1 = ScheduleExpressionBuilder.cron(minute="0", hour="8")

            # Every Monday at 9:15 AM UTC
            expr2 = ScheduleExpressionBuilder.cron(
                minute="15",
                hour="9",
                day_of_week="MON"
            )
            ```
        """
        cron_expr = f"{minute} {hour} {day_of_month} {
            month} {day_of_week} {year}"
        return ScheduleExpression(f"cron({cron_expr})")

    @staticmethod
    def every_n_minutes(n: int) -> ScheduleExpression:
        """Create a rate expression for every n minutes.

        Args:
            n: Number of minutes

        Returns:
            ScheduleExpression: Rate expression for n-minute interval
        """
        unit = TimeUnit.MINUTE if n == 1 else TimeUnit.MINUTES
        return ScheduleExpressionBuilder.rate(n, unit)

    @staticmethod
    def every_n_hours(n: int) -> ScheduleExpression:
        """Create a rate expression for every n hours.

        Args:
            n: Number of hours

        Returns:
            ScheduleExpression: Rate expression for n-hour interval
        """
        unit = TimeUnit.HOUR if n == 1 else TimeUnit.HOURS
        return ScheduleExpressionBuilder.rate(n, unit)

    @staticmethod
    def every_n_days(n: int) -> ScheduleExpression:
        """Create a rate expression for every n days.

        Args:
            n: Number of days

        Returns:
            ScheduleExpression: Rate expression for n-day interval
        """
        unit = TimeUnit.DAY if n == 1 else TimeUnit.DAYS
        return ScheduleExpressionBuilder.rate(n, unit)

    @staticmethod
    def daily_at(hour: int, minute: int = 0) -> ScheduleExpression:
        """Create a cron expression for daily schedule at specific time.

        Args:
            hour: Hour of day (0-23)
            minute: Minute of hour (0-59)

        Returns:
            ScheduleExpression: Cron expression for daily schedule
        """
        return ScheduleExpressionBuilder.cron(
            minute=str(minute),
            hour=str(hour)
        )

    @staticmethod
    def weekly_on(
        day: Union[str, int],
        hour: int = 0,
        minute: int = 0
    ) -> ScheduleExpression:
        """Create a cron expression for weekly schedule.

        Args:
            day: Day of week (0-6 or SUN-SAT)
            hour: Hour of day (0-23)
            minute: Minute of hour (0-59)

        Returns:
            ScheduleExpression: Cron expression for weekly schedule
        """
        return ScheduleExpressionBuilder.cron(
            minute=str(minute),
            hour=str(hour),
            day_of_week=str(day)
        )

    @staticmethod
    def monthly_on(
        day: int,
        hour: int = 0,
        minute: int = 0
    ) -> ScheduleExpression:
        """Create a cron expression for monthly schedule.

        Args:
            day: Day of month (1-31)
            hour: Hour of day (0-23)
            minute: Minute of hour (0-59)

        Returns:
            ScheduleExpression: Cron expression for monthly schedule
        """
        return ScheduleExpressionBuilder.cron(
            minute=str(minute),
            hour=str(hour),
            day_of_month=str(day)
        )


class SchedulerAPIConfig(BaseModel):
    """Configuration for Scheduler API."""

    region: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None

    max_retries: int = Field(
        3,
        description="Maximum number of API call retries",
    )
    timeout: int = Field(
        30,
        description="Timeout for API calls in seconds",
    )

    def to_lambda_config(self) -> LambdaAPIConfig:
        """Convert to Lambda config."""
        return LambdaAPIConfig(
            region=self.region,
            credentials=self.credentials,
        )


class ScheduleRequest(BaseModel):
    """Schedule creation request."""

    name: str
    group_name: str
    schedule_expression: ScheduleExpression
    lambda_function_arn: str
    description: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None


class ScheduleResponse(BaseModel):
    """Schedule response."""

    name: str
    arn: str
    state: str
    group_name: str
    schedule_expression: str
    description: Optional[str] = None
    next_invocation: Optional[datetime] = None
    last_invocation: Optional[datetime] = None
    target_arn: str


class ScheduleListResponse(BaseModel):
    """Schedule list response."""

    schedules: List[Dict[str, Any]]
    next_token: Optional[str] = None

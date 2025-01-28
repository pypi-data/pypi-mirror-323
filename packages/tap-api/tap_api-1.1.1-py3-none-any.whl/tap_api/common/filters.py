"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from abc import ABC
from datetime import datetime, timedelta
from enum import Enum

from tap_api.web.parameter import Parameter


def _format_interval(duration: timedelta) -> str:
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    duration_str = "P"
    if hours or minutes or seconds:
        duration_str += "T"
        if hours:
            duration_str += f"{hours}H"
        if minutes:
            duration_str += f"{minutes}M"
        if seconds:
            duration_str += f"{seconds}S"
    return duration_str


class TimeParameter(Parameter, ABC):
    """
    Abstract base class for time-related parameters.
    """
    pass


class TimeInterval(TimeParameter, ABC):
    """
    Abstract base class for different types of time intervals.
    """

    def __init__(self):
        pass


class StartEndInterval(TimeInterval):
    """
    Represents a time interval with a start and end time.

    For example:
    2020-05-01T12:00:00Z/2020-05-01T13:00:00Z - an hour interval, beginning at noon UTC on 05-01-2020.
    """

    def __init__(self, start: datetime, end: datetime):
        super().__init__()
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return f"{self.start.isoformat()}/{self.end.isoformat()}"


class StartOffsetInterval(TimeInterval):
    """
    Represents a time interval with a start time and a duration.

    For example:
    2020-05-01T12:00:00-0000/PT30M - The thirty minutes beginning at noon UTC on 05-01-2020 and ending at 12:30pm UTC.
    """

    def __init__(self, start: datetime, offset: timedelta):
        super().__init__()
        self.__start = start
        self.__offset = offset

    def __str__(self) -> str:
        return f"{self.__start.isoformat()}/{_format_interval(self.__offset)}"


class OffsetEndInterval(TimeInterval):
    """
    Represents a time interval with a duration and an end time.

    For example:
    PT30M/2020-05-01T12:30:00-0000 - The thirty minutes beginning at noon UTC on 05-01-2020 and ending at 12:30pm UTC.
    """

    def __init__(self, duration: timedelta, end: datetime):
        super().__init__()
        self.__offset = duration
        self.__end = end

    def __str__(self) -> str:
        return f"{_format_interval(self.__offset)}/{self.__end.isoformat()}"


class SinceTime(TimeParameter):
    """
    Represents a specific point in time.

    Example:
    2020-05-01T12:00:00Z - A specific UTC time.
    """

    def __init__(self, dt: datetime):
        self.__dt = dt

    def __str__(self) -> str:
        return self.__dt.isoformat()


class SinceSeconds(TimeParameter):
    """
    Represents a duration in seconds since a reference point.

    Example:
    3600 - Represents 1 hour since a reference point.
    """

    def __init__(self, seconds: int):
        self.__seconds = seconds

    def __str__(self) -> str:
        return str(self.__seconds)


class TimeWindow(Enum):
    DAYS_14 = 14
    DAYS_30 = 30
    DAYS_90 = 90


class ThreatType(Enum):
    URL = 'url'
    ATTACHMENT = 'attachment'
    MESSAGE_TEXT = 'messageText'


class ThreatStatus(Enum):
    ACTIVE = 'active'
    CLEARED = 'cleared'
    FALSE_POSITIVE = 'falsePositive'

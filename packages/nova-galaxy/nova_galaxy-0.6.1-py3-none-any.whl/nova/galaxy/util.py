"""Utilities."""

from enum import Enum


class WorkState(Enum):
    """The state of a tool in Galaxy."""

    NOT_STARTED = 1
    UPLOADING_DATA = 2
    QUEUED = 3
    RUNNING = 4
    FINISHED = 5
    ERROR = 6

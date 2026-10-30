"""Pydantic data models for standardized toolkit findings and reports."""

from enum import Enum


class Severity(str, Enum):
    """Finding severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @classmethod
    def from_str(cls, val: str) -> "Severity":
        val = val.lower().strip()
        for member in cls:
            if member.value == val:
                return member
        return cls.LOW


class Confidence(str, Enum):
    """Finding confidence levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

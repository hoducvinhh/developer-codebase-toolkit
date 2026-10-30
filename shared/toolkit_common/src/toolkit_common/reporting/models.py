"""Pydantic data models for standardized toolkit findings and reports."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


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


class Finding(BaseModel):
    """An individual issue, violation, or metric finding."""
    rule_id: str
    severity: Severity = Severity.MEDIUM
    confidence: Confidence = Confidence.HIGH
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    symbol: Optional[str] = None
    suggestion: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Summary(BaseModel):
    """Aggregate statistics for a report."""
    total_findings: int = 0
    blocking_findings: int = 0
    by_severity: Dict[str, int] = Field(
        default_factory=lambda: {"critical": 0, "high": 0, "medium": 0, "low": 0}
    )
    files_scanned: int = 0
    execution_time_ms: Optional[float] = None


class Report(BaseModel):
    """Unified report model output by all CLI tools."""
    tool: str
    version: str = "0.1.0"
    project: str = "project"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    summary: Summary = Field(default_factory=Summary)
    findings: List[Finding] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def recompute_summary(self, blocking_severities: Optional[List[Severity]] = None) -> None:
        """Recalculate summary totals based on findings list."""
        if blocking_severities is None:
            blocking_severities = [Severity.HIGH, Severity.CRITICAL]

        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        blocking = 0

        for f in self.findings:
            sev_str = f.severity.value
            counts[sev_str] = counts.get(sev_str, 0) + 1
            if f.severity in blocking_severities:
                blocking += 1

        self.summary.total_findings = len(self.findings)
        self.summary.blocking_findings = blocking
        self.summary.by_severity = counts

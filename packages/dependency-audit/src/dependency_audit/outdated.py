"""Outdated dependency detection and SemVer distance measurement."""

from typing import List, Optional

from packaging.version import InvalidVersion, Version
from pydantic import BaseModel

from dependency_audit.models import DependencyItem


class OutdatedItem(BaseModel):
    package: str
    current_version: str
    latest_version: str
    distance: str  # major, minor, patch, unknown


def calculate_version_distance(current: str, latest: str) -> str:
    """Calculate semver distance (major, minor, patch)."""
    try:
        v_curr = Version(current)
        v_latest = Version(latest)
        if v_curr >= v_latest:
            return "up-to-date"

        if v_curr.major != v_latest.major:
            return "major"
        elif v_curr.minor != v_latest.minor:
            return "minor"
        elif v_curr.micro != v_latest.micro:
            return "patch"
        return "minor"
    except InvalidVersion:
        return "unknown"


def check_outdated_dependencies(
    items: List[DependencyItem],
    latest_lookup: Optional[dict] = None,
) -> List[OutdatedItem]:
    """Check for outdated dependencies using a lookup map or mock."""
    outdated: List[OutdatedItem] = []
    lookup = latest_lookup or {}

    for item in items:
        if item.name in lookup:
            latest_ver = lookup[item.name]
            dist = calculate_version_distance(item.version, latest_ver)
            if dist in ("major", "minor", "patch"):
                outdated.append(
                    OutdatedItem(
                        package=item.name,
                        current_version=item.version,
                        latest_version=latest_ver,
                        distance=dist,
                    )
                )

    return outdated

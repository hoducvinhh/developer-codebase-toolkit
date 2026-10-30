"""Data models for dependency inventories, vulnerabilities, and license policies."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class DependencyItem(BaseModel):
    name: str
    version: str
    ecosystem: str  # PyPI, npm
    is_direct: bool = True
    scope: str = "prod"  # prod, dev
    license: Optional[str] = None
    manifest_file: str


class Vulnerability(BaseModel):
    id: str
    package: str
    ecosystem: str
    affected_version: str
    summary: str
    severity: str = "high"
    fixed_version: Optional[str] = None


class InventoryResult(BaseModel):
    dependencies: List[DependencyItem] = Field(default_factory=list)
    duplicates: Dict[str, List[str]] = Field(default_factory=dict)

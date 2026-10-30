"""Committed and unmasked secrets scanner for environment files and code."""

from pathlib import Path
from typing import List

from pydantic import BaseModel
from toolkit_common.filesystem.walker import SafeWalker
from toolkit_common.secrets.redactor import SecretRedactor

from env_checker.parser import parse_env_file


class SecretFinding(BaseModel):
    file: str
    line: int
    key: str
    message: str


def audit_env_secrets(file_path: str | Path) -> List[SecretFinding]:
    """Scan a specific env file for actual secrets populated in plaintext."""
    findings: List[SecretFinding] = []
    p = Path(file_path).resolve()
    if not p.is_file():
        return findings

    res = parse_env_file(p)
    for key, entry in res.variables.items():
        if entry.is_empty:
            continue
        if SecretRedactor.is_secret_value(key, entry.value):
            findings.append(
                SecretFinding(
                    file=str(p),
                    line=entry.line,
                    key=key,
                    message=f"Environment variable '{key}' contains high-entropy or patterned secret in plaintext",
                )
            )

    return findings


def audit_repository_secrets(root_dir: str | Path) -> List[SecretFinding]:
    """Scan all environment files in repository for exposed credentials."""
    root = Path(root_dir).resolve()
    walker = SafeWalker(root=root)
    findings: List[SecretFinding] = []

    # Find env files
    for f in walker.walk_files():
        if f.name.startswith(".env") or f.name.endswith(".env"):
            # Check if this file contains real secrets
            findings.extend(audit_env_secrets(f))

    return findings

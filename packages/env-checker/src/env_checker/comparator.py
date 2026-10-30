"""Comparison of environment template and actual env configurations."""

from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

from env_checker.parser import parse_env_file


class ComparisonResult(BaseModel):
    template_file: str
    target_file: str
    missing_in_target: List[str] = Field(default_factory=list)
    extra_in_target: List[str] = Field(default_factory=list)
    empty_in_target: List[str] = Field(default_factory=list)
    matching_keys: List[str] = Field(default_factory=list)


def compare_env_files(template_path: str | Path, target_path: str | Path) -> ComparisonResult:
    """Compare a template (.env.example) against a concrete target (.env)."""
    tpl = parse_env_file(template_path)
    tgt = parse_env_file(target_path)

    tpl_keys = set(tpl.variables.keys())
    tgt_keys = set(tgt.variables.keys())

    missing = sorted(list(tpl_keys - tgt_keys))
    extra = sorted(list(tgt_keys - tpl_keys))
    matching = sorted(list(tpl_keys & tgt_keys))

    empty = [k for k in matching if tgt.variables[k].is_empty]

    return ComparisonResult(
        template_file=str(template_path),
        target_file=str(target_path),
        missing_in_target=missing,
        extra_in_target=extra,
        empty_in_target=empty,
        matching_keys=matching,
    )

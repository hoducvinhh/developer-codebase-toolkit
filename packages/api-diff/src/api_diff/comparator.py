"""Overall API comparison orchestrator."""

from typing import Any, Dict, List

from pydantic import BaseModel, Field

from api_diff.auth_diff import diff_security
from api_diff.classifier import ApiChange, ChangeCategory
from api_diff.endpoint_diff import diff_endpoints
from api_diff.schema_diff import diff_schemas


class DiffSummary(BaseModel):
    total_changes: int = 0
    breaking: int = 0
    potentially_breaking: int = 0
    non_breaking: int = 0
    informational: int = 0


class DiffResult(BaseModel):
    changes: List[ApiChange] = Field(default_factory=list)
    summary: DiffSummary = Field(default_factory=DiffSummary)

    @classmethod
    def compare(cls, old_spec: Dict[str, Any], new_spec: Dict[str, Any]) -> "DiffResult":
        all_changes: List[ApiChange] = []
        all_changes.extend(diff_endpoints(old_spec, new_spec))
        all_changes.extend(diff_schemas(old_spec, new_spec))
        all_changes.extend(diff_security(old_spec, new_spec))

        b_count = sum(1 for c in all_changes if c.category == ChangeCategory.BREAKING)
        pb_count = sum(1 for c in all_changes if c.category == ChangeCategory.POTENTIALLY_BREAKING)
        nb_count = sum(1 for c in all_changes if c.category == ChangeCategory.NON_BREAKING)
        info_count = sum(1 for c in all_changes if c.category == ChangeCategory.INFORMATIONAL)

        return cls(
            changes=all_changes,
            summary=DiffSummary(
                total_changes=len(all_changes),
                breaking=b_count,
                potentially_breaking=pb_count,
                non_breaking=nb_count,
                informational=info_count,
            ),
        )

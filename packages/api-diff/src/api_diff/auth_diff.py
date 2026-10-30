"""Authentication and security scheme comparison."""

from typing import Any, Dict, List

from api_diff.classifier import ApiChange, ChangeCategory


def diff_security(old_spec: Dict[str, Any], new_spec: Dict[str, Any]) -> List[ApiChange]:
    """Compare global and component security definitions."""
    changes: List[ApiChange] = []

    old_sec = old_spec.get("components", {}).get("securitySchemes", {}) or {}
    new_sec = new_spec.get("components", {}).get("securitySchemes", {}) or {}

    for name in old_sec:
        if name not in new_sec:
            changes.append(
                ApiChange(
                    category=ChangeCategory.BREAKING,
                    path="components.securitySchemes",
                    change_type="SECURITY_SCHEME_REMOVED",
                    message=f"Security scheme '{name}' was removed",
                )
            )

    for name in new_sec:
        if name not in old_sec:
            changes.append(
                ApiChange(
                    category=ChangeCategory.NON_BREAKING,
                    path="components.securitySchemes",
                    change_type="SECURITY_SCHEME_ADDED",
                    message=f"Security scheme '{name}' was added",
                )
            )

    # Check root-level security requirements
    old_root_sec = old_spec.get("security", [])
    new_root_sec = new_spec.get("security", [])
    if not old_root_sec and new_root_sec:
        changes.append(
            ApiChange(
                category=ChangeCategory.BREAKING,
                path="security",
                change_type="GLOBAL_SECURITY_ENFORCED",
                message="Global security requirement was added to API",
            )
        )

    return changes

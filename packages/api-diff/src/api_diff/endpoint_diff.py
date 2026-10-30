"""Endpoint and HTTP operation diffing."""

from typing import Any, Dict, List

from api_diff.classifier import ApiChange, ChangeCategory

HTTP_METHODS = {"get", "post", "put", "delete", "patch", "options", "head"}


def diff_endpoints(old_spec: Dict[str, Any], new_spec: Dict[str, Any]) -> List[ApiChange]:
    """Compare paths, HTTP methods, and operation parameters."""
    changes: List[ApiChange] = []
    old_paths: Dict[str, Any] = old_spec.get("paths", {}) or {}
    new_paths: Dict[str, Any] = new_spec.get("paths", {}) or {}

    # Check for removed paths
    for path, old_item in old_paths.items():
        if path not in new_paths:
            changes.append(
                ApiChange(
                    category=ChangeCategory.BREAKING,
                    path=path,
                    change_type="ENDPOINT_REMOVED",
                    message=f"Endpoint '{path}' was removed",
                )
            )
            continue

        new_item = new_paths[path]
        # Check HTTP methods
        for method in HTTP_METHODS:
            old_op = old_item.get(method)
            new_op = new_item.get(method)

            if old_op and not new_op:
                changes.append(
                    ApiChange(
                        category=ChangeCategory.BREAKING,
                        path=path,
                        method=method.upper(),
                        change_type="METHOD_REMOVED",
                        message=f"HTTP method '{method.upper()} {path}' was removed",
                    )
                )
            elif not old_op and new_op:
                changes.append(
                    ApiChange(
                        category=ChangeCategory.NON_BREAKING,
                        path=path,
                        method=method.upper(),
                        change_type="METHOD_ADDED",
                        message=f"HTTP method '{method.upper()} {path}' was added",
                    )
                )
            elif old_op and new_op:
                # Compare parameters
                changes.extend(diff_parameters(path, method.upper(), old_op.get("parameters", []), new_op.get("parameters", [])))

    # Check for added paths
    for path in new_paths:
        if path not in old_paths:
            changes.append(
                ApiChange(
                    category=ChangeCategory.NON_BREAKING,
                    path=path,
                    change_type="ENDPOINT_ADDED",
                    message=f"New endpoint '{path}' was added",
                )
            )

    return changes


def diff_parameters(path: str, method: str, old_params: List[Dict[str, Any]], new_params: List[Dict[str, Any]]) -> List[ApiChange]:
    """Compare operation parameters."""
    changes: List[ApiChange] = []
    old_p_map = {f"{p.get('in', '')}:{p.get('name', '')}": p for p in old_params if isinstance(p, dict)}
    new_p_map = {f"{p.get('in', '')}:{p.get('name', '')}": p for p in new_params if isinstance(p, dict)}

    for key, old_p in old_p_map.items():
        p_name = old_p.get("name", "")
        p_in = old_p.get("in", "")
        if key not in new_p_map:
            changes.append(
                ApiChange(
                    category=ChangeCategory.BREAKING if old_p.get("required") else ChangeCategory.POTENTIALLY_BREAKING,
                    path=path,
                    method=method,
                    change_type="PARAMETER_REMOVED",
                    message=f"Parameter '{p_name}' in {p_in} was removed",
                )
            )
        else:
            new_p = new_p_map[key]
            # Check required change
            if not old_p.get("required") and new_p.get("required"):
                changes.append(
                    ApiChange(
                        category=ChangeCategory.BREAKING,
                        path=path,
                        method=method,
                        change_type="PARAMETER_NOW_REQUIRED",
                        message=f"Parameter '{p_name}' in {p_in} is now required",
                    )
                )

    for key, new_p in new_p_map.items():
        if key not in old_p_map:
            p_name = new_p.get("name", "")
            p_in = new_p.get("in", "")
            if new_p.get("required"):
                changes.append(
                    ApiChange(
                        category=ChangeCategory.BREAKING,
                        path=path,
                        method=method,
                        change_type="REQUIRED_PARAMETER_ADDED",
                        message=f"New required parameter '{p_name}' in {p_in} was added",
                    )
                )
            else:
                changes.append(
                    ApiChange(
                        category=ChangeCategory.NON_BREAKING,
                        path=path,
                        method=method,
                        change_type="OPTIONAL_PARAMETER_ADDED",
                        message=f"New optional parameter '{p_name}' in {p_in} was added",
                    )
                )

    return changes

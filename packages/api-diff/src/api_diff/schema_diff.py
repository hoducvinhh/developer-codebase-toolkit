"""Request body and response schema comparison."""

from typing import Any, Dict, List

from api_diff.classifier import ApiChange, ChangeCategory

HTTP_METHODS = {"get", "post", "put", "delete", "patch"}


def diff_schemas(old_spec: Dict[str, Any], new_spec: Dict[str, Any]) -> List[ApiChange]:
    """Compare request and response schemas across all endpoints."""
    changes: List[ApiChange] = []
    old_paths: Dict[str, Any] = old_spec.get("paths", {}) or {}
    new_paths: Dict[str, Any] = new_spec.get("paths", {}) or {}

    for path, old_item in old_paths.items():
        if path not in new_paths:
            continue
        new_item = new_paths[path]

        for method in HTTP_METHODS:
            old_op = old_item.get(method)
            new_op = new_item.get(method)
            if not old_op or not new_op:
                continue

            # Compare Request Body
            old_req_schema = _extract_body_schema(old_op)
            new_req_schema = _extract_body_schema(new_op)
            if old_req_schema or new_req_schema:
                changes.extend(_diff_request_schema(path, method.upper(), old_req_schema, new_req_schema))

            # Compare Responses
            old_resps: Dict[str, Any] = old_op.get("responses", {}) or {}
            new_resps: Dict[str, Any] = new_op.get("responses", {}) or {}
            changes.extend(_diff_responses(path, method.upper(), old_resps, new_resps))

    return changes


def _extract_body_schema(op: Dict[str, Any]) -> Dict[str, Any]:
    rb = op.get("requestBody", {})
    if isinstance(rb, dict):
        content = rb.get("content", {})
        json_media = content.get("application/json", {})
        return json_media.get("schema", {})
    return {}


def _diff_request_schema(path: str, method: str, old_schema: Dict[str, Any], new_schema: Dict[str, Any]) -> List[ApiChange]:
    changes: List[ApiChange] = []
    old_props = old_schema.get("properties", {}) if isinstance(old_schema, dict) else {}
    new_props = new_schema.get("properties", {}) if isinstance(new_schema, dict) else {}
    new_req = set(new_schema.get("required", []) if isinstance(new_schema, dict) else [])

    for prop_name, new_prop_spec in new_props.items():
        if prop_name not in old_props:
            if prop_name in new_req:
                changes.append(
                    ApiChange(
                        category=ChangeCategory.BREAKING,
                        path=path,
                        method=method,
                        change_type="REQUIRED_REQUEST_FIELD_ADDED",
                        message=f"Added required field '{prop_name}' to request body",
                    )
                )
            else:
                changes.append(
                    ApiChange(
                        category=ChangeCategory.NON_BREAKING,
                        path=path,
                        method=method,
                        change_type="OPTIONAL_REQUEST_FIELD_ADDED",
                        message=f"Added optional field '{prop_name}' to request body",
                    )
                )
        else:
            # Check type change
            old_type = old_props[prop_name].get("type") if isinstance(old_props[prop_name], dict) else None
            new_type = new_prop_spec.get("type") if isinstance(new_prop_spec, dict) else None
            if old_type and new_type and old_type != new_type:
                changes.append(
                    ApiChange(
                        category=ChangeCategory.BREAKING,
                        path=path,
                        method=method,
                        change_type="REQUEST_FIELD_TYPE_CHANGED",
                        message=f"Request field '{prop_name}' changed type from '{old_type}' to '{new_type}'",
                        old_value=old_type,
                        new_value=new_type,
                    )
                )

    return changes


def _diff_responses(path: str, method: str, old_resps: Dict[str, Any], new_resps: Dict[str, Any]) -> List[ApiChange]:
    changes: List[ApiChange] = []
    for code, old_resp in old_resps.items():
        if code not in new_resps:
            changes.append(
                ApiChange(
                    category=ChangeCategory.BREAKING,
                    path=path,
                    method=method,
                    change_type="RESPONSE_STATUS_REMOVED",
                    message=f"Response status code '{code}' was removed",
                )
            )
            continue

        # Check response properties
        new_resp = new_resps[code]
        old_schema = _extract_resp_schema(old_resp)
        new_schema = _extract_resp_schema(new_resp)

        old_props = old_schema.get("properties", {}) if isinstance(old_schema, dict) else {}
        new_props = new_schema.get("properties", {}) if isinstance(new_schema, dict) else {}

        # Removing a response property is BREAKING for consumers
        for p_name, p_spec in old_props.items():
            if p_name not in new_props:
                changes.append(
                    ApiChange(
                        category=ChangeCategory.BREAKING,
                        path=path,
                        method=method,
                        change_type="RESPONSE_PROPERTY_REMOVED",
                        message=f"Response property '{p_name}' for status {code} was removed",
                    )
                )
            else:
                old_type = p_spec.get("type") if isinstance(p_spec, dict) else None
                new_type = new_props[p_name].get("type") if isinstance(new_props[p_name], dict) else None
                if old_type and new_type and old_type != new_type:
                    changes.append(
                        ApiChange(
                            category=ChangeCategory.BREAKING,
                            path=path,
                            method=method,
                            change_type="RESPONSE_PROPERTY_TYPE_CHANGED",
                            message=f"Response property '{p_name}' status {code} type changed from '{old_type}' to '{new_type}'",
                            old_value=old_type,
                            new_value=new_type,
                        )
                    )

        # Adding a response property is NON_BREAKING
        for p_name in new_props:
            if p_name not in old_props:
                changes.append(
                    ApiChange(
                        category=ChangeCategory.NON_BREAKING,
                        path=path,
                        method=method,
                        change_type="RESPONSE_PROPERTY_ADDED",
                        message=f"Response property '{p_name}' was added to status {code}",
                    )
                )

    return changes


def _extract_resp_schema(resp: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(resp, dict):
        content = resp.get("content", {})
        json_media = content.get("application/json", {})
        return json_media.get("schema", {})
    return {}

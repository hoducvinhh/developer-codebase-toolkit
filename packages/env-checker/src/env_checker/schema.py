"""Validation of environment variables against type and constraint schemas."""

import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SchemaRule(BaseModel):
    type: str = "string"  # string, integer, float, boolean, url, email, port, enum
    required: bool = False
    allowed_values: Optional[List[str]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    regex: Optional[str] = None
    description: Optional[str] = None


class ValidationError(BaseModel):
    key: str
    line: Optional[int] = None
    rule: str
    message: str


def validate_variable(key: str, val: str, rule: SchemaRule, line: Optional[int] = None) -> Optional[ValidationError]:
    """Validate a single variable value against a SchemaRule."""
    if not val:
        if rule.required:
            return ValidationError(key=key, line=line, rule="required", message=f"Required variable '{key}' is empty or missing")
        return None

    t = rule.type.lower()
    if t in ("int", "integer"):
        try:
            num = int(val)
            if rule.min_value is not None and num < rule.min_value:
                return ValidationError(key=key, line=line, rule="min_value", message=f"'{key}' ({num}) is less than minimum {rule.min_value}")
            if rule.max_value is not None and num > rule.max_value:
                return ValidationError(key=key, line=line, rule="max_value", message=f"'{key}' ({num}) exceeds maximum {rule.max_value}")
        except ValueError:
            return ValidationError(key=key, line=line, rule="type_integer", message=f"'{key}' value '{val}' is not a valid integer")

    elif t == "float":
        try:
            num = float(val)
            if rule.min_value is not None and num < rule.min_value:
                return ValidationError(key=key, line=line, rule="min_value", message=f"'{key}' ({num}) is less than minimum {rule.min_value}")
            if rule.max_value is not None and num > rule.max_value:
                return ValidationError(key=key, line=line, rule="max_value", message=f"'{key}' ({num}) exceeds maximum {rule.max_value}")
        except ValueError:
            return ValidationError(key=key, line=line, rule="type_float", message=f"'{key}' value '{val}' is not a valid float")

    elif t in ("bool", "boolean"):
        if val.lower() not in ("true", "false", "1", "0", "yes", "no", "y", "n"):
            return ValidationError(key=key, line=line, rule="type_boolean", message=f"'{key}' value '{val}' is not a valid boolean (expected true/false/1/0)")

    elif t == "port":
        try:
            port = int(val)
            if not (1 <= port <= 65535):
                return ValidationError(key=key, line=line, rule="port_range", message=f"'{key}' port {port} out of range (1-65535)")
        except ValueError:
            return ValidationError(key=key, line=line, rule="type_port", message=f"'{key}' value '{val}' is not a valid port number")

    elif t == "url":
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://\S+$", val):
            return ValidationError(key=key, line=line, rule="type_url", message=f"'{key}' value '{val}' is not a valid URL")

    elif t == "email":
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", val):
            return ValidationError(key=key, line=line, rule="type_email", message=f"'{key}' value '{val}' is not a valid email address")

    elif t == "enum":
        if rule.allowed_values and val not in rule.allowed_values:
            return ValidationError(key=key, line=line, rule="enum_values", message=f"'{key}' value '{val}' is not in allowed values: {rule.allowed_values}")

    if rule.regex:
        if not re.search(rule.regex, val):
            return ValidationError(key=key, line=line, rule="regex_match", message=f"'{key}' value '{val}' does not match regex pattern: {rule.regex}")

    return None


def validate_env_against_schema(variables: Dict[str, Any], schema_data: Dict[str, Any]) -> List[ValidationError]:
    """Validate parsed variables dictionary against schema specification."""
    errors: List[ValidationError] = []
    rules_dict = schema_data.get("variables", schema_data)

    for key, spec in rules_dict.items():
        if isinstance(spec, dict):
            rule = SchemaRule(**spec)
        elif isinstance(spec, str):
            rule = SchemaRule(type=spec)
        else:
            continue

        entry = variables.get(key)
        val = entry.value if hasattr(entry, "value") else (str(entry) if entry is not None else "")
        line = entry.line if hasattr(entry, "line") else None

        err = validate_variable(key, val, rule, line)
        if err:
            errors.append(err)

    return errors

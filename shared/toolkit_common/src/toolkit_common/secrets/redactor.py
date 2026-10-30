"""Secret redaction implementation for CLI outputs and reports."""

import re
from typing import Any, Dict

from toolkit_common.secrets.patterns import SECRET_PATTERNS, is_high_entropy_secret

REDACTED_LABEL = "[REDACTED]"

# Words that strongly indicate a secret variable name
SUSPICIOUS_KEYS = {
    "password", "secret", "token", "api_key", "apikey", "private_key",
    "access_token", "auth_token", "client_secret", "jwt_secret",
}


class SecretRedactor:
    """Detects and masks sensitive credentials in strings, dicts, and reports."""

    @classmethod
    def redact_text(cls, text: str) -> str:
        """Scan string and replace all matched secrets with [REDACTED]."""
        if not text:
            return text

        result = text
        for pattern in SECRET_PATTERNS:
            def repl(m: re.Match[str]) -> str:
                # If group 1 matched (e.g. in db uri or key=val), replace group 1
                if m.lastindex and m.lastindex >= 1:
                    full = m.group(0)
                    secret_part = m.group(1)
                    return full.replace(secret_part, REDACTED_LABEL)
                return REDACTED_LABEL

            result = pattern.sub(repl, result)

        return result

    @classmethod
    def is_secret_value(cls, key_name: str, value: str) -> bool:
        """Check if a given key-value pair represents a secret."""
        normalized_key = key_name.lower().replace("-", "_")
        if any(susp in normalized_key for susp in SUSPICIOUS_KEYS):
            return True

        for pattern in SECRET_PATTERNS:
            if pattern.search(value):
                return True

        if is_high_entropy_secret(value):
            return True

        return False

    @classmethod
    def redact_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Deep copy and mask sensitive values in a dictionary."""
        cleaned: Dict[str, Any] = {}
        for k, v in data.items():
            if isinstance(v, dict):
                cleaned[k] = cls.redact_dict(v)
            elif isinstance(v, list):
                cleaned[k] = [cls.redact_dict(item) if isinstance(item, dict) else cls.redact_text(str(item)) for item in v]
            elif isinstance(v, str):
                if cls.is_secret_value(k, v):
                    cleaned[k] = REDACTED_LABEL
                else:
                    cleaned[k] = cls.redact_text(v)
            else:
                cleaned[k] = v
        return cleaned

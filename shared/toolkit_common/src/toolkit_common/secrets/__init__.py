"""Secret detection and masking module."""

from toolkit_common.secrets.patterns import SECRET_PATTERNS, is_high_entropy_secret, shannon_entropy
from toolkit_common.secrets.redactor import REDACTED_LABEL, SecretRedactor

__all__ = [
    "SecretRedactor",
    "REDACTED_LABEL",
    "SECRET_PATTERNS",
    "shannon_entropy",
    "is_high_entropy_secret",
]

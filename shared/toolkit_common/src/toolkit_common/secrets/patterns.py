"""Regular expression patterns and entropy calculation for secret detection."""

import math
import re
from typing import List, Pattern

SECRET_PATTERNS: List[Pattern[str]] = [
    # AWS Keys
    re.compile(r"(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}"),
    # GitHub Tokens
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,255}"),
    # Generic Private Keys
    re.compile(r"-----BEGIN\s+[A-Z\s]+PRIVATE\s+KEY-----[\s\S]*?-----END\s+[A-Z\s]+PRIVATE\s+KEY-----"),
    # Slack Tokens
    re.compile(r"xox[baprs]-[0-9a-zA-Z]{10,48}"),
    # Generic Bearer Tokens / Authorization headers
    re.compile(r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}"),
    # DB URI Passwords: postgres://user:password@host
    re.compile(r"(?i)(?:postgres|postgresql|mysql|mongodb|redis|amqp):\/\/[^:\s]+:([^@\s]+)@"),
    # Key / Secret / Token assignments
    re.compile(r"""(?i)(?:api_key|apikey|secret|password|passwd|auth_token|access_token|private_key)\s*[:=]\s*['"]?([a-zA-Z0-9_\-.~!@#$%^&*+=]{12,})['"]?"""),
    # JWT Tokens
    re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_\-.]{10,}"),
]


def shannon_entropy(data: str) -> float:
    """Calculate the Shannon entropy of a string."""
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    for x in set(data):
        p_x = float(data.count(x)) / length
        entropy += - p_x * math.log2(p_x)
    return entropy


def is_high_entropy_secret(token: str, min_len: int = 16, min_entropy: float = 3.6) -> bool:
    """Determine if a token is likely a high-entropy secret (e.g. hex/base64 key)."""
    clean = token.strip().strip("'\"")
    if len(clean) < min_len:
        return False
    # Avoid matching regular prose/words by checking entropy
    return shannon_entropy(clean) >= min_entropy

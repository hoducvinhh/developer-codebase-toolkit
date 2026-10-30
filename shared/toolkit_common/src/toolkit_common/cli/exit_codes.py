"""Exit code standards for all CLI tools in the toolkit."""

from enum import IntEnum


class ExitCode(IntEnum):
    """Standardized process exit codes."""
    SUCCESS = 0
    BLOCKING_FINDINGS = 1
    INVALID_CONFIG = 2
    RUNTIME_ERROR = 3
    UNSUPPORTED = 4

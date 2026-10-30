"""JSON report formatter."""

import json

from toolkit_common.reporting.models import Report


class JsonFormatter:
    """Format report as indented JSON."""

    @staticmethod
    def format(report: Report, indent: int = 2) -> str:
        return json.dumps(report.model_dump(), indent=indent)

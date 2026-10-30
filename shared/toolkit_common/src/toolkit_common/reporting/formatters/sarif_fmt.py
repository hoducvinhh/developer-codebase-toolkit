"""SARIF (Static Analysis Results Interchange Format) v2.1.0 formatter."""

import json
from typing import Any, Dict, List

from toolkit_common.reporting.models import Report, Severity


class SarifFormatter:
    """Format report into SARIF v2.1.0 JSON format."""

    SEV_MAP = {
        Severity.CRITICAL: "error",
        Severity.HIGH: "error",
        Severity.MEDIUM: "warning",
        Severity.LOW: "note",
    }

    @classmethod
    def format(cls, report: Report) -> str:
        rule_ids = set()
        rules: List[Dict[str, Any]] = []

        for f in report.findings:
            if f.rule_id not in rule_ids:
                rule_ids.add(f.rule_id)
                rules.append({
                    "id": f.rule_id,
                    "name": f.rule_id,
                    "shortDescription": {"text": f.message[:120]},
                    "defaultConfiguration": {
                        "level": cls.SEV_MAP.get(f.severity, "warning")
                    }
                })

        results: List[Dict[str, Any]] = []
        for f in report.findings:
            res: Dict[str, Any] = {
                "ruleId": f.rule_id,
                "level": cls.SEV_MAP.get(f.severity, "warning"),
                "message": {"text": f.message},
            }
            if f.file:
                start_line = f.line or 1
                start_col = f.column or 1
                res["locations"] = [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": f.file.replace("\\", "/")
                            },
                            "region": {
                                "startLine": start_line,
                                "startColumn": start_col
                            }
                        }
                    }
                ]
            results.append(res)

        sarif_doc = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": report.tool,
                            "version": report.version,
                            "rules": rules
                        }
                    },
                    "results": results
                }
            ]
        }
        return json.dumps(sarif_doc, indent=2)

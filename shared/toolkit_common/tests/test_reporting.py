import json

from toolkit_common.reporting.formatters import (
    JsonFormatter,
    MarkdownFormatter,
    SarifFormatter,
    TerminalFormatter,
)
from toolkit_common.reporting.models import Confidence, Finding, Report, Severity


def test_report_models_and_summary():
    report = Report(tool="test-tool", project="demo-project")
    report.findings.append(
        Finding(
            rule_id="RULE-01",
            severity=Severity.HIGH,
            confidence=Confidence.HIGH,
            message="Critical flaw found",
            file="src/index.ts",
            line=10,
        )
    )
    report.findings.append(
        Finding(
            rule_id="RULE-02",
            severity=Severity.LOW,
            confidence=Confidence.MEDIUM,
            message="Minor style warning",
            file="src/util.ts",
            line=5,
        )
    )

    report.recompute_summary()
    assert report.summary.total_findings == 2
    assert report.summary.blocking_findings == 1
    assert report.summary.by_severity["high"] == 1
    assert report.summary.by_severity["low"] == 1


def test_formatters():
    report = Report(tool="test-tool", project="demo-project")
    report.findings.append(
        Finding(
            rule_id="SEC-001",
            severity=Severity.CRITICAL,
            message="Hardcoded API key detected",
            file="config.py",
            line=42,
        )
    )
    report.recompute_summary()

    # JSON Formatter
    json_out = JsonFormatter.format(report)
    parsed = json.loads(json_out)
    assert parsed["tool"] == "test-tool"
    assert len(parsed["findings"]) == 1

    # Markdown Formatter
    md_out = MarkdownFormatter.format(report)
    assert "# Analysis Report: `test-tool`" in md_out
    assert "`SEC-001`" in md_out

    # SARIF Formatter
    sarif_out = SarifFormatter.format(report)
    sarif_data = json.loads(sarif_out)
    assert sarif_data["version"] == "2.1.0"
    assert sarif_data["runs"][0]["tool"]["driver"]["name"] == "test-tool"
    assert len(sarif_data["runs"][0]["results"]) == 1
    assert sarif_data["runs"][0]["results"][0]["ruleId"] == "SEC-001"

    # Terminal Formatter
    plain_out = TerminalFormatter.format(report, no_color=True)
    assert "SEC-001" in plain_out
    rich_out = TerminalFormatter.format(report, no_color=False)
    assert "SEC-001" in rich_out

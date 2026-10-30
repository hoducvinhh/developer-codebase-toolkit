"""Markdown report formatter for GitHub pull requests and documentation."""

from toolkit_common.reporting.models import Report


class MarkdownFormatter:
    """Format report as GitHub Flavored Markdown."""

    @staticmethod
    def format(report: Report) -> str:
        lines = []
        lines.append(f"# Analysis Report: `{report.tool}`")
        lines.append("")
        lines.append(f"- **Project:** `{report.project}`")
        lines.append(f"- **Timestamp:** `{report.timestamp}`")
        lines.append(f"- **Total Findings:** {report.summary.total_findings}")
        lines.append(f"- **Blocking Issues:** {report.summary.blocking_findings}")
        lines.append("")

        lines.append("## Summary by Severity")
        lines.append("")
        lines.append("| Severity | Count |")
        lines.append("| :--- | :--- |")
        for sev in ["critical", "high", "medium", "low"]:
            count = report.summary.by_severity.get(sev, 0)
            lines.append(f"| **{sev.capitalize()}** | {count} |")
        lines.append("")

        if report.findings:
            lines.append("## Findings Detail")
            lines.append("")
            lines.append("| Rule | Severity | Confidence | Location | Message |")
            lines.append("| :--- | :--- | :--- | :--- | :--- |")
            for f in report.findings:
                loc = f.file or "-"
                if f.line is not None:
                    loc += f":{f.line}"
                    if f.column is not None:
                        loc += f":{f.column}"
                clean_msg = f.message.replace("|", "\\|")
                lines.append(f"| `{f.rule_id}` | `{f.severity.value}` | `{f.confidence.value}` | `{loc}` | {clean_msg} |")
            lines.append("")

        if report.metadata:
            lines.append("## Metadata")
            lines.append("")
            for k, v in report.metadata.items():
                lines.append(f"- **{k}:** `{v}`")
            lines.append("")

        return "\n".join(lines)

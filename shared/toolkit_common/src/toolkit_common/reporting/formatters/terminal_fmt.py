"""Terminal formatter with Rich tables and plain-text fallback."""

import io

from toolkit_common.reporting.models import Report, Severity

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


class TerminalFormatter:
    """Renders reports for interactive terminal output."""

    SEV_COLORS = {
        Severity.CRITICAL: "bold red",
        Severity.HIGH: "red",
        Severity.MEDIUM: "yellow",
        Severity.LOW: "cyan",
    }

    @classmethod
    def format(cls, report: Report, no_color: bool = False) -> str:
        if HAS_RICH and not no_color:
            return cls._format_rich(report)
        return cls._format_plain(report)

    @classmethod
    def _format_rich(cls, report: Report) -> str:
        buf = io.StringIO()
        console = Console(file=buf, force_terminal=True, color_system="standard")

        # Title banner
        title_text = f"Tool: [bold]{report.tool}[/bold] v{report.version} | Project: [green]{report.project}[/green]"
        console.print(Panel(title_text, title="Analysis Complete", expand=False))

        # Summary Table
        summary_table = Table(title="Summary", show_header=True, header_style="bold magenta")
        summary_table.add_column("Total Findings", justify="center")
        summary_table.add_column("Blocking", justify="center")
        summary_table.add_column("Critical", justify="center", style="bold red")
        summary_table.add_column("High", justify="center", style="red")
        summary_table.add_column("Medium", justify="center", style="yellow")
        summary_table.add_column("Low", justify="center", style="cyan")

        s = report.summary
        summary_table.add_row(
            str(s.total_findings),
            str(s.blocking_findings),
            str(s.by_severity.get("critical", 0)),
            str(s.by_severity.get("high", 0)),
            str(s.by_severity.get("medium", 0)),
            str(s.by_severity.get("low", 0)),
        )
        console.print(summary_table)

        # Findings Table
        if report.findings:
            findings_table = Table(title="Findings", show_header=True, header_style="bold cyan")
            findings_table.add_column("Rule", style="dim", no_wrap=True)
            findings_table.add_column("Severity", justify="center")
            findings_table.add_column("Location")
            findings_table.add_column("Message")

            for f in report.findings:
                loc = f.file or "-"
                if f.line is not None:
                    loc += f":{f.line}"

                color = cls.SEV_COLORS.get(f.severity, "white")
                sev_badge = f"[{color}]{f.severity.value.upper()}[/{color}]"
                findings_table.add_row(f.rule_id, sev_badge, loc, f.message)

            console.print(findings_table)

        return buf.getvalue().rstrip()

    @classmethod
    def _format_plain(cls, report: Report) -> str:
        lines = []
        lines.append(f"=== {report.tool} v{report.version} (Project: {report.project}) ===")
        lines.append(f"Total findings: {report.summary.total_findings} (Blocking: {report.summary.blocking_findings})")
        lines.append(
            f"Critical: {report.summary.by_severity.get('critical', 0)} | "
            f"High: {report.summary.by_severity.get('high', 0)} | "
            f"Medium: {report.summary.by_severity.get('medium', 0)} | "
            f"Low: {report.summary.by_severity.get('low', 0)}"
        )
        lines.append("-" * 70)

        if report.findings:
            for f in report.findings:
                loc = f.file or "-"
                if f.line is not None:
                    loc += f":{f.line}"
                lines.append(f"[{f.severity.value.upper()}] {f.rule_id} at {loc}")
                lines.append(f"  {f.message}")
                if f.suggestion:
                    lines.append(f"  Suggestion: {f.suggestion}")
            lines.append("-" * 70)

        return "\n".join(lines)

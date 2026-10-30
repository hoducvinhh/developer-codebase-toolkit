"""API Diff (api-diff) CLI implementation."""

import sys
from pathlib import Path

import click
from toolkit_common.cli.base import common_options
from toolkit_common.cli.exit_codes import ExitCode
from toolkit_common.reporting.formatters import (
    JsonFormatter,
    MarkdownFormatter,
    SarifFormatter,
    TerminalFormatter,
)
from toolkit_common.reporting.models import Confidence, Finding, Report, Severity

from api_diff.classifier import ChangeCategory
from api_diff.comparator import DiffResult
from api_diff.parser import OpenApiParser


@click.command()
@click.argument("old_spec", type=click.Path(exists=True, dir_okay=False))
@click.argument("new_spec", type=click.Path(exists=True, dir_okay=False))
@click.option("--fail-on", type=click.Choice(["breaking", "potentially_breaking", "none"], case_sensitive=False), default="breaking")
@common_options
def main(old_spec: str, new_spec: str, fail_on: str, output_format: str, output: str, config: str, quiet: bool, verbose: bool, no_color: bool) -> None:
    """Compare OpenAPI specifications and detect breaking changes."""
    try:
        old_p = OpenApiParser.from_file(old_spec)
        new_p = OpenApiParser.from_file(new_spec)

        result = DiffResult.compare(old_p.resolved_spec, new_p.resolved_spec)

        report = Report(
            tool="api-diff",
            version="0.1.0",
            project=f"{Path(old_spec).name} -> {Path(new_spec).name}",
            metadata={
                "old_spec": old_spec,
                "new_spec": new_spec,
                "breaking_count": result.summary.breaking,
                "potentially_breaking_count": result.summary.potentially_breaking,
                "non_breaking_count": result.summary.non_breaking,
            },
        )

        for c in result.changes:
            sev = Severity.LOW
            if c.category == ChangeCategory.BREAKING:
                sev = Severity.CRITICAL
            elif c.category == ChangeCategory.POTENTIALLY_BREAKING:
                sev = Severity.HIGH
            elif c.category == ChangeCategory.NON_BREAKING:
                sev = Severity.LOW

            loc = c.path
            if c.method:
                loc = f"{c.method} {c.path}"

            report.findings.append(
                Finding(
                    rule_id=f"API-{c.change_type}",
                    severity=sev,
                    confidence=Confidence.HIGH,
                    message=c.message,
                    file=loc,
                )
            )

        report.recompute_summary()

        if output_format == "json":
            out_str = JsonFormatter.format(report)
        elif output_format == "markdown":
            out_str = MarkdownFormatter.format(report)
        elif output_format == "sarif":
            out_str = SarifFormatter.format(report)
        else:
            out_str = TerminalFormatter.format(report, no_color=no_color)

        if output:
            Path(output).write_text(out_str, encoding="utf-8")
        else:
            if not quiet:
                click.echo(out_str)

        should_fail = False
        if fail_on == "breaking" and result.summary.breaking > 0:
            should_fail = True
        elif fail_on == "potentially_breaking" and (result.summary.breaking > 0 or result.summary.potentially_breaking > 0):
            should_fail = True

        sys.exit(ExitCode.BLOCKING_FINDINGS if should_fail else ExitCode.SUCCESS)

    except Exception as e:
        if verbose:
            import traceback
            traceback.print_exc()
        click.echo(f"Error during API comparison: {e}", err=True)
        sys.exit(ExitCode.RUNTIME_ERROR)


if __name__ == "__main__":
    main()

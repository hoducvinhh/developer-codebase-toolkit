"""Dead Code Finder (dcf) CLI implementation."""

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
from toolkit_common.reporting.models import Report

from dead_code_finder.analyzer import DeadCodeAnalyzer


@click.group()
@click.version_option(version="0.1.0", prog_name="dcf")
def main() -> None:
    """Dead and unused code detection CLI."""
    pass


@main.command("scan")
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--min-confidence", type=click.Choice(["low", "medium", "high"], case_sensitive=False), default="low", help="Filter findings by minimum confidence level.")
@click.option("--include-exports", is_flag=True, default=False, help="Flag potentially unused public exports.")
@click.option("--fail-on-findings", is_flag=True, default=False, help="Exit with code 1 if any high confidence dead code is detected.")
@common_options
def scan(directory: str, min_confidence: str, include_exports: bool, fail_on_findings: bool, output_format: str, output: str, config: str, quiet: bool, verbose: bool, no_color: bool) -> None:
    """Scan directory for unused imports, variables, functions, and unreachable code."""
    try:
        target_dir = Path(directory).resolve()
        analyzer = DeadCodeAnalyzer(
            root_dir=target_dir,
            include_exports=include_exports,
            min_confidence=min_confidence,
        )
        findings = analyzer.scan()

        report = Report(
            tool="dead-code-finder",
            version="0.1.0",
            project=target_dir.name,
            findings=findings,
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

        if fail_on_findings and report.summary.blocking_findings > 0:
            sys.exit(ExitCode.BLOCKING_FINDINGS)
        sys.exit(ExitCode.SUCCESS)

    except Exception as e:
        if verbose:
            import traceback
            traceback.print_exc()
        click.echo(f"Error: {e}", err=True)
        sys.exit(ExitCode.RUNTIME_ERROR)


if __name__ == "__main__":
    main()

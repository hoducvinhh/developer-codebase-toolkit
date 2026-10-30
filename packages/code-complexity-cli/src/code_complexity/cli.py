"""Code Complexity (ccx) CLI implementation."""

import sys
from pathlib import Path
from typing import List

import click
from toolkit_common.cli.base import common_options
from toolkit_common.cli.exit_codes import ExitCode
from toolkit_common.config.loader import load_config_file
from toolkit_common.filesystem.walker import SafeWalker
from toolkit_common.reporting.formatters import (
    JsonFormatter,
    MarkdownFormatter,
    SarifFormatter,
    TerminalFormatter,
)
from toolkit_common.reporting.models import Report, Summary

from code_complexity.metrics import ComplexityThresholds, FunctionMetrics
from code_complexity.ranker import analyze_python_file, generate_threshold_findings, rank_hotspots


@click.group()
@click.version_option(version="0.1.0", prog_name="ccx")
def main() -> None:
    """Measure code complexity, nesting, and maintainability hotspots."""
    pass


@main.command("report")
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--fail-on-threshold", is_flag=True, default=False, help="Exit with code 1 if complexity thresholds are exceeded.")
@common_options
def report_command(directory: str, fail_on_threshold: bool, output_format: str, output: str, config: str, quiet: bool, verbose: bool, no_color: bool) -> None:
    """Run full codebase complexity audit and verify thresholds."""
    try:
        target_dir = Path(directory).resolve()
        thresholds = ComplexityThresholds()
        cfg_path = Path(config) if config else (target_dir / "ccx.yml")
        if cfg_path.is_file():
            cfg_data = load_config_file(cfg_path)
            thresholds = ComplexityThresholds(**cfg_data.get("thresholds", cfg_data))

        walker = SafeWalker(root=target_dir)
        py_files = list(walker.walk_files(extensions=[".py"]))

        all_functions: List[FunctionMetrics] = []
        for pf in py_files:
            file_m = analyze_python_file(pf)
            all_functions.extend(file_m.functions)

        findings = generate_threshold_findings(all_functions, thresholds)

        report = Report(
            tool="code-complexity-cli",
            version="0.1.0",
            project=target_dir.name,
            summary=Summary(
                files_scanned=len(py_files),
                total_findings=len(findings),
            ),
            findings=findings,
            metadata={
                "total_functions_analyzed": len(all_functions),
                "threshold_max_cyclomatic": thresholds.max_cyclomatic,
                "threshold_max_cognitive": thresholds.max_cognitive,
            },
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

        if fail_on_threshold and report.summary.blocking_findings > 0:
            sys.exit(ExitCode.BLOCKING_FINDINGS)
        sys.exit(ExitCode.SUCCESS)

    except Exception as e:
        if verbose:
            import traceback
            traceback.print_exc()
        click.echo(f"Error: {e}", err=True)
        sys.exit(ExitCode.RUNTIME_ERROR)


@main.command("hotspots")
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--top", "-n", type=int, default=10, help="Number of top complex hotspots to display.")
@common_options
def hotspots_command(directory: str, top: int, output_format: str, output: str, config: str, quiet: bool, verbose: bool, no_color: bool) -> None:
    """Identify and rank top maintainability hotspots."""
    try:
        target_dir = Path(directory).resolve()
        walker = SafeWalker(root=target_dir)
        py_files = list(walker.walk_files(extensions=[".py"]))

        all_functions: List[FunctionMetrics] = []
        for pf in py_files:
            file_m = analyze_python_file(pf)
            all_functions.extend(file_m.functions)

        ranked = rank_hotspots(all_functions, top_n=top)

        if output_format == "json":
            import json
            out_str = json.dumps([f.model_dump() for f in ranked], indent=2)
        else:
            lines = [f"=== Top {len(ranked)} Complexity Hotspots in {target_dir.name} ==="]
            lines.append(f"{'Rank':<5} {'Function':<24} {'File':<25} {'Cyc':<6} {'Cog':<6} {'LOC':<6}")
            lines.append("-" * 75)
            for idx, fn in enumerate(ranked):
                fname = fn.name[:22]
                fpath = Path(fn.file).name[:23]
                lines.append(f"#{idx+1:<4} {fname:<24} {fpath:<25} {fn.cyclomatic_complexity:<6} {fn.cognitive_complexity:<6} {fn.loc:<6}")
            out_str = "\n".join(lines)

        if output:
            Path(output).write_text(out_str, encoding="utf-8")
        else:
            if not quiet:
                click.echo(out_str)
        sys.exit(ExitCode.SUCCESS)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(ExitCode.RUNTIME_ERROR)


@main.command("analyze")
@click.argument("file_path", type=click.Path(exists=True, dir_okay=False))
@common_options
def analyze_command(file_path: str, output_format: str, output: str, config: str, quiet: bool, verbose: bool, no_color: bool) -> None:
    """Analyze a single source code file in detail."""
    try:
        target_file = Path(file_path).resolve()
        metrics = analyze_python_file(target_file)

        if output_format == "json":
            out_str = metrics.model_dump_json(indent=2)
        else:
            lines = [
                f"=== File Complexity Analysis: {target_file.name} ===",
                f"Total LOC: {metrics.loc}",
                f"Total Cyclomatic: {metrics.total_cyclomatic}",
                f"Total Cognitive: {metrics.total_cognitive}",
                f"Functions ({len(metrics.functions)}):",
            ]
            for fn in metrics.functions:
                lines.append(f"  - {fn.name} (L{fn.start_line}-L{fn.end_line}): Cyclomatic={fn.cyclomatic_complexity}, Cognitive={fn.cognitive_complexity}, LOC={fn.loc}, Params={fn.parameter_count}, Nesting={fn.max_nesting_depth}")
            out_str = "\n".join(lines)

        if output:
            Path(output).write_text(out_str, encoding="utf-8")
        else:
            if not quiet:
                click.echo(out_str)
        sys.exit(ExitCode.SUCCESS)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(ExitCode.RUNTIME_ERROR)


if __name__ == "__main__":
    main()

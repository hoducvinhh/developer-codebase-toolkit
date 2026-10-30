"""Codebase Map (cbm) CLI implementation."""

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
from toolkit_common.reporting.models import Confidence, Finding, Report, Severity, Summary

from codebase_map.dependencies import analyze_dependencies
from codebase_map.discovery import discover_repository
from codebase_map.entrypoints import detect_entrypoints
from codebase_map.mermaid import generate_mermaid_diagram
from codebase_map.modules import detect_modules
from codebase_map.tree import build_tree, render_tree_text


@click.group()
@click.version_option(version="0.1.0", prog_name="cbm")
def main() -> None:
    """Codebase structure, architecture, and dependency visualization."""
    pass


@main.command()
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@common_options
def analyze(directory: str, output_format: str, output: str, config: str, quiet: bool, verbose: bool, no_color: bool) -> None:
    """Run comprehensive codebase architecture and structure analysis."""
    try:
        target_dir = Path(directory).resolve()
        disc = discover_repository(target_dir)
        modules = detect_modules(target_dir)
        entrypoints = detect_entrypoints(target_dir)

        report = Report(
            tool="codebase-map",
            version="0.1.0",
            project=target_dir.name,
            summary=Summary(
                files_scanned=disc.total_files,
                total_findings=len(entrypoints),
            ),
            metadata={
                "root": str(target_dir),
                "primary_language": disc.primary_language,
                "frameworks": disc.frameworks,
                "manifests": disc.manifests,
                "modules_count": len(modules),
                "total_lines": disc.total_lines,
            },
        )

        for ep in entrypoints:
            report.findings.append(
                Finding(
                    rule_id="CBM-ENTRYPOINT",
                    severity=Severity.LOW,
                    confidence=Confidence.HIGH if ep.confidence == "High" else Confidence.MEDIUM,
                    message=f"Detected {ep.kind}: {', '.join(ep.evidence)}",
                    file=ep.file,
                )
            )

        report.recompute_summary()

        # Format and output
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
            if not quiet:
                click.echo(f"Report written to {output}")
        else:
            if not quiet:
                click.echo(out_str)

        sys.exit(ExitCode.SUCCESS)
    except Exception as e:
        if verbose:
            import traceback
            traceback.print_exc()
        click.echo(f"Error during analysis: {e}", err=True)
        sys.exit(ExitCode.RUNTIME_ERROR)


@main.command()
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--depth", "-d", type=int, default=3, help="Max depth for directory tree rendering.")
@common_options
def tree(directory: str, depth: int, output_format: str, output: str, config: str, quiet: bool, verbose: bool, no_color: bool) -> None:
    """Display file tree hierarchy and statistics."""
    try:
        target_dir = Path(directory).resolve()
        root_node = build_tree(target_dir, max_depth=depth)

        if output_format == "json":
            out_str = root_node.model_dump_json(indent=2)
        else:
            out_str = render_tree_text(root_node)

        if output:
            Path(output).write_text(out_str, encoding="utf-8")
        else:
            if not quiet:
                click.echo(out_str)
        sys.exit(ExitCode.SUCCESS)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(ExitCode.RUNTIME_ERROR)


@main.command()
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@common_options
def deps(directory: str, output_format: str, output: str, config: str, quiet: bool, verbose: bool, no_color: bool) -> None:
    """Extract and analyze internal module and external package dependencies."""
    try:
        target_dir = Path(directory).resolve()
        graph = analyze_dependencies(target_dir)

        if output_format == "json":
            out_str = graph.model_dump_json(indent=2)
        else:
            lines = [
                f"=== Dependencies for {target_dir.name} ===",
                f"Internal modules ({len(graph.internal_modules)}):",
                *[f"  - {m}" for m in graph.internal_modules[:20]],
                f"External packages ({len(graph.external_packages)}):",
                *[f"  - {p}" for p in graph.external_packages[:20]],
                f"Total dependency links: {len(graph.edges)}",
            ]
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


@main.command()
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--direction", type=click.Choice(["TD", "LR"], case_sensitive=False), default="TD")
@click.option("--output", "-o", type=click.Path(writable=True))
def diagram(directory: str, direction: str, output: str) -> None:
    """Generate Mermaid architecture diagram."""
    try:
        target_dir = Path(directory).resolve()
        modules = detect_modules(target_dir)
        graph = analyze_dependencies(target_dir)
        chart = generate_mermaid_diagram(graph, modules, direction=direction)

        if output:
            Path(output).write_text(chart, encoding="utf-8")
        else:
            click.echo(chart)
        sys.exit(ExitCode.SUCCESS)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(ExitCode.RUNTIME_ERROR)


if __name__ == "__main__":
    main()

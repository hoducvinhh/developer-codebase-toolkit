"""Environment Checker (envcheck) CLI implementation."""

import sys
from pathlib import Path
from typing import List, Optional

import click
from toolkit_common.cli.base import common_options
from toolkit_common.cli.exit_codes import ExitCode
from toolkit_common.config.loader import load_config_file
from toolkit_common.reporting.formatters import (
    JsonFormatter,
    MarkdownFormatter,
    SarifFormatter,
    TerminalFormatter,
)
from toolkit_common.reporting.models import Confidence, Finding, Report, Severity

from env_checker.comparator import compare_env_files
from env_checker.parser import parse_env_file
from env_checker.schema import validate_env_against_schema
from env_checker.secrets import audit_repository_secrets
from env_checker.usage_scanner import scan_codebase_usages


class DefaultGroup(click.Group):
    """Click group that defaults to 'audit' command when no recognized command is given."""
    def parse_args(self, ctx: click.Context, args: List[str]) -> List[str]:
        if not args:
            args = ["audit"]
        elif args[0] not in self.commands and args[0] not in ("--help", "-h", "--version"):
            args = ["audit"] + args
        return super().parse_args(ctx, args)


@click.group(cls=DefaultGroup)
@click.version_option(version="0.1.0", prog_name="envcheck")
def main() -> None:
    """Environment configuration validator and secret auditor."""
    pass


@main.command("audit")
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--fail-on", type=click.Choice(["any", "missing", "secret", "schema"], case_sensitive=False), default="missing")
@common_options
def audit_command(directory: str, fail_on: str, output_format: str, output: str, config: str, quiet: bool, verbose: bool, no_color: bool) -> None:
    """Run full environment audit: compare .env with template, validate schema, and check secrets."""
    try:
        target_dir = Path(directory).resolve()
        template_file = target_dir / ".env.example"
        env_file = target_dir / ".env"
        schema_file = Path(config) if config else (target_dir / "envcheck.yml")

        report = Report(tool="env-checker", version="0.1.0", project=target_dir.name)

        # 1. Compare template vs actual
        if template_file.is_file() and env_file.is_file():
            comp = compare_env_files(template_file, env_file)
            for m in comp.missing_in_target:
                report.findings.append(
                    Finding(
                        rule_id="ENV-MISSING",
                        severity=Severity.HIGH,
                        confidence=Confidence.HIGH,
                        message=f"Missing variable '{m}' defined in .env.example",
                        file=str(env_file),
                        suggestion=f"Define '{m}' in {env_file.name}",
                    )
                )
            for e in comp.empty_in_target:
                report.findings.append(
                    Finding(
                        rule_id="ENV-EMPTY",
                        severity=Severity.MEDIUM,
                        confidence=Confidence.HIGH,
                        message=f"Variable '{e}' is empty in {env_file.name}",
                        file=str(env_file),
                    )
                )

        # 2. Schema validation
        if schema_file.is_file() and env_file.is_file():
            schema_data = load_config_file(schema_file)
            parsed_env = parse_env_file(env_file)
            errs = validate_env_against_schema(parsed_env.variables, schema_data)
            for err in errs:
                report.findings.append(
                    Finding(
                        rule_id=f"ENV-SCHEMA-{err.rule.upper()}",
                        severity=Severity.HIGH,
                        confidence=Confidence.HIGH,
                        message=err.message,
                        file=str(env_file),
                        line=err.line,
                    )
                )

        # 3. Secret exposure
        sec_findings = audit_repository_secrets(target_dir)
        for sf in sec_findings:
            report.findings.append(
                Finding(
                    rule_id="ENV-SECRET-EXPOSED",
                    severity=Severity.CRITICAL,
                    confidence=Confidence.HIGH,
                    message=sf.message,
                    file=sf.file,
                    line=sf.line,
                    suggestion="Move secret value to encrypted secrets store or use dummy test key in repository",
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

        if report.summary.blocking_findings > 0:
            sys.exit(ExitCode.BLOCKING_FINDINGS)
        sys.exit(ExitCode.SUCCESS)

    except Exception as e:
        if verbose:
            import traceback
            traceback.print_exc()
        click.echo(f"Error: {e}", err=True)
        sys.exit(ExitCode.RUNTIME_ERROR)


@main.command("compare")
@click.argument("template", type=click.Path(exists=True, dir_okay=False))
@click.argument("target", type=click.Path(exists=True, dir_okay=False))
@common_options
def compare(template: str, target: str, output_format: str, output: str, config: str, quiet: bool, verbose: bool, no_color: bool) -> None:
    """Compare a template .env file against a concrete target .env."""
    try:
        res = compare_env_files(template, target)
        report = Report(tool="env-checker", version="0.1.0", project=Path(target).name)

        for m in res.missing_in_target:
            report.findings.append(
                Finding(
                    rule_id="ENV-MISSING",
                    severity=Severity.HIGH,
                    confidence=Confidence.HIGH,
                    message=f"Missing variable '{m}' (defined in {template})",
                    file=target,
                )
            )
        for ex in res.extra_in_target:
            report.findings.append(
                Finding(
                    rule_id="ENV-EXTRA",
                    severity=Severity.LOW,
                    confidence=Confidence.HIGH,
                    message=f"Undocumented variable '{ex}' present in target",
                    file=target,
                )
            )

        report.recompute_summary()
        if output_format == "json":
            out_str = JsonFormatter.format(report)
        else:
            out_str = TerminalFormatter.format(report, no_color=no_color)

        if output:
            Path(output).write_text(out_str, encoding="utf-8")
        else:
            if not quiet:
                click.echo(out_str)

        sys.exit(ExitCode.BLOCKING_FINDINGS if report.summary.blocking_findings > 0 else ExitCode.SUCCESS)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(ExitCode.RUNTIME_ERROR)


@main.command("validate")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--schema", "-s", "schema_path", required=True, type=click.Path(exists=True, dir_okay=False))
@common_options
def validate(env_file: str, schema_path: str, output_format: str, output: str, config: str, quiet: bool, verbose: bool, no_color: bool) -> None:
    """Validate environment variables against a schema specification."""
    try:
        parsed_env = parse_env_file(env_file)
        schema_data = load_config_file(schema_path)
        errs = validate_env_against_schema(parsed_env.variables, schema_data)

        report = Report(tool="env-checker", version="0.1.0", project=Path(env_file).name)
        for err in errs:
            report.findings.append(
                Finding(
                    rule_id=f"ENV-SCHEMA-{err.rule.upper()}",
                    severity=Severity.HIGH,
                    confidence=Confidence.HIGH,
                    message=err.message,
                    file=env_file,
                    line=err.line,
                )
            )

        report.recompute_summary()
        if output_format == "json":
            out_str = JsonFormatter.format(report)
        else:
            out_str = TerminalFormatter.format(report, no_color=no_color)

        if output:
            Path(output).write_text(out_str, encoding="utf-8")
        else:
            if not quiet:
                click.echo(out_str)

        sys.exit(ExitCode.BLOCKING_FINDINGS if report.summary.blocking_findings > 0 else ExitCode.SUCCESS)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(ExitCode.RUNTIME_ERROR)


@main.command("analyze-usage")
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--template", "-t", type=click.Path(exists=True, dir_okay=False), default=None)
@common_options
def analyze_usage(directory: str, template: Optional[str], output_format: str, output: str, config: str, quiet: bool, verbose: bool, no_color: bool) -> None:
    """Scan source code for environment variable usages and cross-check against template."""
    try:
        target_dir = Path(directory).resolve()
        usages = scan_codebase_usages(target_dir)

        template_keys = set()
        tpl_path = Path(template) if template else (target_dir / ".env.example")
        if tpl_path.is_file():
            template_keys = set(parse_env_file(tpl_path).variables.keys())

        report = Report(tool="env-checker", version="0.1.0", project=target_dir.name)

        for u in usages:
            if template_keys and u.variable not in template_keys:
                report.findings.append(
                    Finding(
                        rule_id="ENV-UNDECLARED-USAGE",
                        severity=Severity.MEDIUM,
                        confidence=Confidence.HIGH,
                        message=f"Variable '{u.variable}' accessed in code but not documented in {tpl_path.name}",
                        file=u.file,
                        line=u.line,
                    )
                )

        report.recompute_summary()
        if output_format == "json":
            out_str = JsonFormatter.format(report)
        else:
            out_str = TerminalFormatter.format(report, no_color=no_color)

        if output:
            Path(output).write_text(out_str, encoding="utf-8")
        else:
            if not quiet:
                click.echo(out_str)

        sys.exit(ExitCode.SUCCESS)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(ExitCode.RUNTIME_ERROR)


@main.command("secrets")
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@common_options
def secrets(directory: str, output_format: str, output: str, config: str, quiet: bool, verbose: bool, no_color: bool) -> None:
    """Scan environment files and repository for unmasked plaintext secrets."""
    try:
        target_dir = Path(directory).resolve()
        sec_findings = audit_repository_secrets(target_dir)

        report = Report(tool="env-checker", version="0.1.0", project=target_dir.name)
        for sf in sec_findings:
            report.findings.append(
                Finding(
                    rule_id="ENV-SECRET-EXPOSED",
                    severity=Severity.CRITICAL,
                    confidence=Confidence.HIGH,
                    message=sf.message,
                    file=sf.file,
                    line=sf.line,
                )
            )

        report.recompute_summary()
        if output_format == "json":
            out_str = JsonFormatter.format(report)
        else:
            out_str = TerminalFormatter.format(report, no_color=no_color)

        if output:
            Path(output).write_text(out_str, encoding="utf-8")
        else:
            if not quiet:
                click.echo(out_str)

        sys.exit(ExitCode.BLOCKING_FINDINGS if report.summary.blocking_findings > 0 else ExitCode.SUCCESS)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(ExitCode.RUNTIME_ERROR)


if __name__ == "__main__":
    main()

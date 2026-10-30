"""Dependency Audit (da) CLI implementation."""

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

from dependency_audit.licenses import check_license_compliance
from dependency_audit.manifests.inventory import collect_inventory
from dependency_audit.osv_client import OsvClient


@click.group()
@click.version_option(version="0.1.0", prog_name="da")
def main() -> None:
    """Dependency intelligence, vulnerability scanning, and license compliance."""
    pass


@main.command("scan")
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--offline", is_flag=True, default=False, help="Use cached vulnerability data only (no network calls).")
@click.option("--policy", type=click.Choice(["permissive", "copyleft"], case_sensitive=False), default="permissive")
@click.option("--fail-on-vuln", is_flag=True, default=False, help="Exit with code 1 if any vulnerability is found.")
@common_options
def scan(directory: str, offline: bool, policy: str, fail_on_vuln: bool, output_format: str, output: str, config: str, quiet: bool, verbose: bool, no_color: bool) -> None:
    """Run full dependency audit: inventory, duplicate packages, licenses, and vulnerabilities."""
    try:
        target_dir = Path(directory).resolve()
        inv = collect_inventory(target_dir)

        report = Report(
            tool="dependency-audit",
            version="0.1.0",
            project=target_dir.name,
            metadata={
                "total_dependencies": len(inv.dependencies),
                "duplicate_packages_count": len(inv.duplicates),
            },
        )

        # 1. Duplicate packages in tree
        for pkg, versions in inv.duplicates.items():
            report.findings.append(
                Finding(
                    rule_id="DA-DUPLICATE-DEPENDENCY",
                    severity=Severity.LOW,
                    confidence=Confidence.HIGH,
                    symbol=pkg,
                    message=f"Duplicate versions of '{pkg}' detected in dependency tree: {', '.join(versions)}",
                    suggestion="Deduplicate package versions in lockfile",
                )
            )

        # 2. License violations
        lic_violations = check_license_compliance(inv.dependencies, policy=policy)
        for lv in lic_violations:
            report.findings.append(
                Finding(
                    rule_id="DA-LICENSE-VIOLATION",
                    severity=Severity.HIGH,
                    confidence=Confidence.HIGH,
                    symbol=lv.package,
                    message=lv.message,
                    suggestion="Replace with an alternatively licensed library or update company compliance policy",
                )
            )

        # 3. Vulnerability scanning
        cache_path = target_dir / ".osv_cache.json"
        client = OsvClient(cache_file=cache_path, offline=offline)
        vulns = client.check_vulnerabilities(inv.dependencies)
        for v in vulns:
            sev_level = Severity.HIGH if v.severity in ("high", "critical") else Severity.MEDIUM
            msg = f"Vulnerability {v.id} in {v.package}@{v.affected_version}: {v.summary}"
            sug = f"Upgrade to version {v.fixed_version}" if v.fixed_version else "Check vendor security advisory"
            report.findings.append(
                Finding(
                    rule_id=f"DA-VULN-{v.id}",
                    severity=sev_level,
                    confidence=Confidence.HIGH,
                    symbol=v.package,
                    message=msg,
                    suggestion=sug,
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

        if fail_on_vuln and report.summary.blocking_findings > 0:
            sys.exit(ExitCode.BLOCKING_FINDINGS)
        sys.exit(ExitCode.SUCCESS)

    except Exception as e:
        if verbose:
            import traceback
            traceback.print_exc()
        click.echo(f"Error: {e}", err=True)
        sys.exit(ExitCode.RUNTIME_ERROR)


@main.command("audit")
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--offline", is_flag=True, default=False)
@common_options
def audit_command(directory: str, offline: bool, output_format: str, output: str, config: str, quiet: bool, verbose: bool, no_color: bool) -> None:
    """Query OSV database for known vulnerabilities."""
    try:
        target_dir = Path(directory).resolve()
        inv = collect_inventory(target_dir)
        client = OsvClient(cache_file=target_dir / ".osv_cache.json", offline=offline)
        vulns = client.check_vulnerabilities(inv.dependencies)

        report = Report(tool="dependency-audit", version="0.1.0", project=target_dir.name)
        for v in vulns:
            sev_level = Severity.HIGH if v.severity in ("high", "critical") else Severity.MEDIUM
            report.findings.append(
                Finding(
                    rule_id=f"DA-VULN-{v.id}",
                    severity=sev_level,
                    confidence=Confidence.HIGH,
                    symbol=v.package,
                    message=f"[{v.id}] {v.package}@{v.affected_version}: {v.summary}",
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


@main.command("licenses")
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--policy", type=click.Choice(["permissive", "copyleft"], case_sensitive=False), default="permissive")
@common_options
def licenses_command(directory: str, policy: str, output_format: str, output: str, config: str, quiet: bool, verbose: bool, no_color: bool) -> None:
    """Check dependency licenses against compliance policy."""
    try:
        target_dir = Path(directory).resolve()
        inv = collect_inventory(target_dir)
        violations = check_license_compliance(inv.dependencies, policy=policy)

        report = Report(tool="dependency-audit", version="0.1.0", project=target_dir.name)
        for v in violations:
            report.findings.append(
                Finding(
                    rule_id="DA-LICENSE-VIOLATION",
                    severity=Severity.HIGH,
                    confidence=Confidence.HIGH,
                    symbol=v.package,
                    message=v.message,
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

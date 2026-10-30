import json
from pathlib import Path

from click.testing import CliRunner
from dependency_audit.cli import main
from dependency_audit.licenses import check_license_compliance
from dependency_audit.manifests.inventory import collect_inventory
from dependency_audit.models import DependencyItem
from dependency_audit.osv_client import OsvClient
from dependency_audit.outdated import calculate_version_distance


def test_requirements_and_inventory(tmp_path: Path):
    req = tmp_path / "requirements.txt"
    req.write_text("requests==2.28.1\nflask>=2.0.0\n", encoding="utf-8")

    inv = collect_inventory(tmp_path)
    pkg_names = [d.name for d in inv.dependencies]
    assert "requests" in pkg_names
    assert "flask" in pkg_names


def test_package_lock_duplicates(tmp_path: Path):
    lock_file = tmp_path / "package-lock.json"
    lock_data = {
        "name": "sample",
        "packages": {
            "node_modules/lodash": {"version": "4.17.20"},
            "node_modules/dep/node_modules/lodash": {"version": "4.17.21"},
        },
    }
    lock_file.write_text(json.dumps(lock_data), encoding="utf-8")

    inv = collect_inventory(tmp_path)
    assert "lodash" in inv.duplicates
    assert len(inv.duplicates["lodash"]) == 2


def test_license_compliance():
    items = [
        DependencyItem(name="requests", version="2.28.1", ecosystem="PyPI", manifest_file=""),
        DependencyItem(name="gpl-sample-pkg", version="1.0.0", ecosystem="PyPI", manifest_file="", license="GPL-3.0"),
    ]
    violations = check_license_compliance(items, policy="permissive")
    assert len(violations) == 1
    assert violations[0].package == "gpl-sample-pkg"


def test_version_distance():
    assert calculate_version_distance("1.0.0", "2.0.0") == "major"
    assert calculate_version_distance("1.2.0", "1.3.0") == "minor"
    assert calculate_version_distance("1.2.3", "1.2.4") == "patch"
    assert calculate_version_distance("2.0.0", "1.9.9") == "up-to-date"


def test_osv_offline_cache(tmp_path: Path):
    cache_file = tmp_path / ".osv_cache.json"
    cache_data = {
        "PyPI:vulnerable-pkg:1.0.0": [
            {
                "id": "GHSA-1234-5678",
                "summary": "Remote Code Execution vulnerability",
                "database_specific": {"severity": "CRITICAL"},
            }
        ]
    }
    cache_file.write_text(json.dumps(cache_data), encoding="utf-8")

    client = OsvClient(cache_file=cache_file, offline=True)
    items = [DependencyItem(name="vulnerable-pkg", version="1.0.0", ecosystem="PyPI", manifest_file="")]
    vulns = client.check_vulnerabilities(items)

    assert len(vulns) == 1
    assert vulns[0].id == "GHSA-1234-5678"


def test_da_cli(tmp_path: Path):
    req = tmp_path / "requirements.txt"
    req.write_text("requests==2.28.1\n", encoding="utf-8")

    runner = CliRunner()
    res_scan = runner.invoke(main, ["scan", str(tmp_path), "--offline", "--format", "json"])
    assert res_scan.exit_code == 0
    assert "dependency-audit" in res_scan.output

    res_audit = runner.invoke(main, ["audit", str(tmp_path), "--offline"])
    assert res_audit.exit_code == 0

    res_lic = runner.invoke(main, ["licenses", str(tmp_path)])
    assert res_lic.exit_code == 0

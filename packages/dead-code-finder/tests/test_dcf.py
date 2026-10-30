from pathlib import Path

from click.testing import CliRunner
from dead_code_finder.analyzer import DeadCodeAnalyzer
from dead_code_finder.cli import main


def test_python_dead_code(tmp_path: Path):
    py_file = tmp_path / "example.py"
    py_file.write_text(
        """import sys
import math

def calculate(x):
    unused_local = 10
    return x * 2
    print("Unreachable statement")

def _never_called():
    pass

calculate(5)
""",
        encoding="utf-8",
    )

    analyzer = DeadCodeAnalyzer(tmp_path)
    findings = analyzer.scan()
    rule_ids = [f.rule_id for f in findings]

    assert "DCF-UNUSED-IMPORT" in rule_ids
    assert "DCF-UNUSED-VARIABLE" in rule_ids
    assert "DCF-UNREACHABLE-CODE" in rule_ids
    assert "DCF-UNUSED-PRIVATE-FUNCTION" in rule_ids


def test_js_dead_code(tmp_path: Path):
    js_file = tmp_path / "app.js"
    js_file.write_text(
        """import { unusedFunction, usedFunction } from './module';

console.log(usedFunction());
""",
        encoding="utf-8",
    )

    analyzer = DeadCodeAnalyzer(tmp_path)
    findings = analyzer.scan()
    rule_ids = [f.rule_id for f in findings]

    assert "DCF-UNUSED-IMPORT" in rule_ids
    assert any(f.symbol == "unusedFunction" for f in findings)


def test_cli_scan(tmp_path: Path):
    py_file = tmp_path / "dummy.py"
    py_file.write_text("import os\n", encoding="utf-8")

    runner = CliRunner()
    res = runner.invoke(main, ["scan", str(tmp_path), "--format", "json"])
    assert res.exit_code == 0
    assert "dead-code-finder" in res.output
    assert "DCF-UNUSED-IMPORT" in res.output

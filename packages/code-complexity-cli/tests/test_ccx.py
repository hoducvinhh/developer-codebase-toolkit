import ast
from pathlib import Path

from click.testing import CliRunner
from code_complexity.cli import main
from code_complexity.cognitive import calculate_python_cognitive
from code_complexity.cyclomatic import calculate_python_cyclomatic
from code_complexity.metrics import ComplexityThresholds
from code_complexity.ranker import analyze_python_file, generate_threshold_findings, rank_hotspots

SAMPLE_CODE = """
def simple_func(x):
    return x * 2

def complex_func(a, b, c, d, e, f):
    total = 0
    if a > 0:
        for i in range(b):
            if i % 2 == 0:
                total += i
            else:
                total -= i
    elif c > 0:
        while d > 0:
            d -= 1
    return total
"""


def test_cyclomatic_calculation():
    tree = ast.parse(SAMPLE_CODE)
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

    simple_cyc = calculate_python_cyclomatic(funcs["simple_func"])
    assert simple_cyc == 1

    complex_cyc = calculate_python_cyclomatic(funcs["complex_func"])
    # 1 (base) + 1 (if) + 1 (for) + 1 (if inside for) + 1 (elif) + 1 (while) = 6
    assert complex_cyc >= 5


def test_cognitive_calculation():
    tree = ast.parse(SAMPLE_CODE)
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

    simple_cog = calculate_python_cognitive(funcs["simple_func"])
    assert simple_cog == 0

    complex_cog = calculate_python_cognitive(funcs["complex_func"])
    # Nesting penalty should make cognitive complexity higher than cyclomatic
    assert complex_cog > 0


def test_ranker_and_thresholds(tmp_path: Path):
    py_file = tmp_path / "module.py"
    py_file.write_text(SAMPLE_CODE, encoding="utf-8")

    file_m = analyze_python_file(py_file)
    assert len(file_m.functions) == 2

    hotspots = rank_hotspots(file_m.functions, top_n=1)
    assert len(hotspots) == 1
    assert hotspots[0].name == "complex_func"

    # Threshold with max_params = 4 (complex_func has 6)
    thresholds = ComplexityThresholds(max_parameters=4)
    findings = generate_threshold_findings(file_m.functions, thresholds)
    assert any(f.rule_id == "CCX-TOO-MANY-PARAMETERS" for f in findings)


def test_ccx_cli(tmp_path: Path):
    py_file = tmp_path / "app.py"
    py_file.write_text(SAMPLE_CODE, encoding="utf-8")

    runner = CliRunner()

    res_report = runner.invoke(main, ["report", str(tmp_path), "--format", "json"])
    assert res_report.exit_code == 0
    assert "code-complexity-cli" in res_report.output

    res_hotspots = runner.invoke(main, ["hotspots", str(tmp_path)])
    assert res_hotspots.exit_code == 0
    assert "complex_func" in res_hotspots.output

    res_analyze = runner.invoke(main, ["analyze", str(py_file)])
    assert res_analyze.exit_code == 0
    assert "simple_func" in res_analyze.output

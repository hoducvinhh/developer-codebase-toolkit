from pathlib import Path

from click.testing import CliRunner
from codebase_map.cli import main
from codebase_map.dependencies import analyze_dependencies
from codebase_map.discovery import discover_repository
from codebase_map.entrypoints import detect_entrypoints
from codebase_map.mermaid import generate_mermaid_diagram
from codebase_map.modules import detect_modules
from codebase_map.tree import build_tree, render_tree_text


def create_sample_repo(tmp_path: Path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "__init__.py").write_text("", encoding="utf-8")
    (src / "main.py").write_text(
        "import os\nfrom src.utils import helper\n\nif __name__ == '__main__':\n    helper()\n",
        encoding="utf-8",
    )
    (src / "utils.py").write_text(
        "def helper():\n    pass\n",
        encoding="utf-8",
    )
    req = tmp_path / "requirements.txt"
    req.write_text("fastapi>=0.100.0\nuvicorn\n", encoding="utf-8")
    return tmp_path


def test_discovery(tmp_path: Path):
    create_sample_repo(tmp_path)
    res = discover_repository(tmp_path)
    assert res.total_files >= 3
    assert "Python" in res.languages
    assert "FastAPI" in res.frameworks
    assert "requirements.txt" in res.manifests


def test_tree_rendering(tmp_path: Path):
    create_sample_repo(tmp_path)
    root_node = build_tree(tmp_path, max_depth=2)
    rendered = render_tree_text(root_node)
    assert "src/" in rendered
    assert "main.py" in rendered


def test_entrypoints(tmp_path: Path):
    create_sample_repo(tmp_path)
    eps = detect_entrypoints(tmp_path)
    assert len(eps) >= 1
    assert any("main.py" in ep.file for ep in eps)


def test_dependencies_and_mermaid(tmp_path: Path):
    create_sample_repo(tmp_path)
    graph = analyze_dependencies(tmp_path)
    modules = detect_modules(tmp_path)
    diagram = generate_mermaid_diagram(graph, modules)
    assert "flowchart" in diagram
    assert "src" in diagram


def test_cli_commands(tmp_path: Path):
    create_sample_repo(tmp_path)
    runner = CliRunner()

    res_analyze = runner.invoke(main, ["analyze", str(tmp_path), "--format", "json"])
    assert res_analyze.exit_code == 0
    assert "codebase-map" in res_analyze.output

    res_tree = runner.invoke(main, ["tree", str(tmp_path)])
    assert res_tree.exit_code == 0
    assert "src/" in res_tree.output

    res_deps = runner.invoke(main, ["deps", str(tmp_path)])
    assert res_deps.exit_code == 0

    res_diag = runner.invoke(main, ["diagram", str(tmp_path)])
    assert res_diag.exit_code == 0
    assert "flowchart" in res_diag.output

from pathlib import Path

from toolkit_common.filesystem.gitignore import GitignoreMatcher
from toolkit_common.filesystem.walker import SafeWalker


def test_gitignore_matcher(tmp_path: Path):
    gi = tmp_path / ".gitignore"
    gi.write_text("*.log\n/build/\n!keep.log\n", encoding="utf-8")

    matcher = GitignoreMatcher.from_file(gi)
    assert matcher.matches(tmp_path / "app.log", is_dir=False) is True
    assert matcher.matches(tmp_path / "keep.log", is_dir=False) is False
    assert matcher.matches(tmp_path / "build", is_dir=True) is True
    assert matcher.matches(tmp_path / "main.py", is_dir=False) is False


def test_safe_walker(tmp_path: Path):
    # Setup test file tree
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("print('hello')", encoding="utf-8")
    (src / "test.js").write_text("console.log(1)", encoding="utf-8")

    ignored_dir = tmp_path / "node_modules"
    ignored_dir.mkdir()
    (ignored_dir / "dep.js").write_text("// dummy", encoding="utf-8")

    walker = SafeWalker(root=tmp_path)
    files = list(walker.walk_files())
    file_names = [f.name for f in files]

    assert "main.py" in file_names
    assert "test.js" in file_names
    assert "dep.js" not in file_names

    # Filter extensions
    py_files = list(walker.walk_files(extensions=[".py"]))
    assert len(py_files) == 1
    assert py_files[0].name == "main.py"

"""Source code scanner for environment variable references."""

import ast
import re
from pathlib import Path
from typing import List

from pydantic import BaseModel
from toolkit_common.filesystem.walker import SafeWalker

JS_ENV_RE = re.compile(
    r"""process\.env\.(?:([a-zA-Z_][a-zA-Z0-9_]*)|\[['"]([a-zA-Z_][a-zA-Z0-9_]*)['"]\])"""
)


class EnvUsage(BaseModel):
    variable: str
    file: str
    line: int
    source_snippet: str


def scan_python_file(path: Path) -> List[EnvUsage]:
    """Scan Python file for os.environ and os.getenv accesses."""
    usages: List[EnvUsage] = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)
    except Exception:
        return usages

    lines = content.splitlines()

    for node in ast.walk(tree):
        var_name = None
        # os.environ[...]
        if isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Attribute) and node.value.attr == "environ":
                if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                    var_name = node.slice.value
        # os.getenv(...) or os.environ.get(...)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "getenv" and node.args:
                    if isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                        var_name = node.args[0].value
                elif node.func.attr == "get" and isinstance(node.func.value, ast.Attribute) and node.func.value.attr == "environ":
                    if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                        var_name = node.args[0].value

        if var_name:
            line_no = node.lineno
            snippet = lines[line_no - 1].strip() if 0 < line_no <= len(lines) else ""
            usages.append(
                EnvUsage(
                    variable=var_name,
                    file=str(path),
                    line=line_no,
                    source_snippet=snippet,
                )
            )

    return usages


def scan_js_file(path: Path) -> List[EnvUsage]:
    """Scan JavaScript / TypeScript file for process.env usages."""
    usages: List[EnvUsage] = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return usages

    lines = content.splitlines()
    for idx, line in enumerate(lines):
        for m in JS_ENV_RE.finditer(line):
            var_name = m.group(1) or m.group(2)
            if var_name:
                usages.append(
                    EnvUsage(
                        variable=var_name,
                        file=str(path),
                        line=idx + 1,
                        source_snippet=line.strip(),
                    )
                )

    return usages


def scan_codebase_usages(root_dir: str | Path) -> List[EnvUsage]:
    """Find all environment variable usages across codebase."""
    root = Path(root_dir).resolve()
    walker = SafeWalker(root=root)
    all_usages: List[EnvUsage] = []

    for f in walker.walk_files(extensions=[".py", ".js", ".ts", ".jsx", ".tsx"]):
        if f.suffix == ".py":
            all_usages.extend(scan_python_file(f))
        else:
            all_usages.extend(scan_js_file(f))

    return all_usages

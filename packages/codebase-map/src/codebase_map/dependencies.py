"""Dependency and import graph analysis."""

import ast
import re
from typing import List

JS_IMPORT_RE = re.compile(
    r"""(?:import\s+(?:[\w*\s{},]*\s+from\s+)?|require\(\s*)['"]([^'"]+)['"]\s*\)?""",
    re.MULTILINE,
)


def parse_python_imports(content: str) -> List[str]:
    """Parse python imports using ast with regex fallback."""
    imports = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
                elif node.level:
                    imports.append("." * node.level)
    except SyntaxError:
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("import "):
                parts = line.replace("import ", "").split(",")
                for p in parts:
                    imports.append(p.strip().split()[0])
            elif line.startswith("from "):
                m = re.match(r"from\s+([a-zA-Z0-9_\.]+)\s+import", line)
                if m:
                    imports.append(m.group(1))
    return imports


def parse_js_imports(content: str) -> List[str]:
    """Parse JavaScript and TypeScript import statements."""
    return [m.group(1) for m in JS_IMPORT_RE.finditer(content)]

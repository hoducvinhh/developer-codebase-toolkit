"""Dependency and import graph analysis."""

import ast
import re
from pathlib import Path
from typing import List, Set

from pydantic import BaseModel, Field
from toolkit_common.filesystem.walker import SafeWalker

JS_IMPORT_RE = re.compile(
    r"""(?:import\s+(?:[\w*\s{},]*\s+from\s+)?|require\(\s*)['"]([^'"]+)['"]\s*\)?""",
    re.MULTILINE,
)


class DependencyNode(BaseModel):
    name: str
    is_internal: bool
    path: str = ""


class DependencyEdge(BaseModel):
    source: str
    target: str
    is_internal: bool


class DependencyGraph(BaseModel):
    nodes: List[DependencyNode] = Field(default_factory=list)
    edges: List[DependencyEdge] = Field(default_factory=list)
    internal_modules: List[str] = Field(default_factory=list)
    external_packages: List[str] = Field(default_factory=list)


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
        # Regex fallback
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


def analyze_dependencies(root_dir: str | Path) -> DependencyGraph:
    """Analyze imports across codebase and construct directed dependency graph."""
    root = Path(root_dir).resolve()
    walker = SafeWalker(root=root)
    files = list(walker.walk_files(extensions=[".py", ".js", ".ts", ".jsx", ".tsx"]))

    file_rel_map = {f: str(f.relative_to(root)).replace("\\", "/") for f in files}
    internal_modules_set: Set[str] = set(file_rel_map.values())
    external_pkgs_set: Set[str] = set()
    edges: List[DependencyEdge] = []

    for f, rel_path in file_rel_map.items():
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        raw_imports: List[str] = []
        if f.suffix == ".py":
            raw_imports = parse_python_imports(content)
        else:
            raw_imports = parse_js_imports(content)

        for imp in raw_imports:
            imp_clean = imp.strip()
            if not imp_clean:
                continue

            # Check if internal import
            is_internal = False
            target_name = imp_clean

            if imp_clean.startswith("."):
                is_internal = True
            elif "/" in imp_clean and (imp_clean.startswith("./") or imp_clean.startswith("../")):
                is_internal = True
            else:
                # Check if root contains a directory or file matching the top-level module
                top_part = imp_clean.split(".")[0]
                possible_dir = root / top_part
                possible_src_dir = root / "src" / top_part
                possible_file = root / f"{top_part}.py"
                if possible_dir.exists() or possible_src_dir.exists() or possible_file.exists():
                    is_internal = True
                else:
                    external_pkgs_set.add(top_part)

            edges.append(
                DependencyEdge(
                    source=rel_path,
                    target=target_name,
                    is_internal=is_internal,
                )
            )

    nodes = [
        DependencyNode(name=mod, is_internal=True, path=mod)
        for mod in sorted(internal_modules_set)
    ] + [
        DependencyNode(name=pkg, is_internal=False, path="")
        for pkg in sorted(external_pkgs_set)
    ]

    return DependencyGraph(
        nodes=nodes,
        edges=edges,
        internal_modules=sorted(list(internal_modules_set)),
        external_packages=sorted(list(external_pkgs_set)),
    )

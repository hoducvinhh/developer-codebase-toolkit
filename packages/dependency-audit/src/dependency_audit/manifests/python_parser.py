"""Python dependencies parser (requirements.txt, pyproject.toml, poetry.lock)."""

import re
from pathlib import Path
from typing import List

from dependency_audit.models import DependencyItem

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

REQ_LINE_RE = re.compile(r"^([a-zA-Z0-9_\-\.]+)(?:([=><~^!]+)([^;\s]+))?")


def parse_requirements_txt(file_path: Path) -> List[DependencyItem]:
    """Parse standard requirements.txt file."""
    items: List[DependencyItem] = []
    if not file_path.is_file():
        return items

    lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        line = re.sub(r"\s+#.*$", "", line).strip()
        m = REQ_LINE_RE.match(line)
        if m:
            pkg_name = m.group(1).lower()
            ver = m.group(3) or "latest"
            items.append(
                DependencyItem(
                    name=pkg_name,
                    version=ver,
                    ecosystem="PyPI",
                    is_direct=True,
                    scope="prod",
                    manifest_file=str(file_path),
                )
            )
    return items


def parse_pyproject_toml(file_path: Path) -> List[DependencyItem]:
    """Parse PEP 621 dependencies from pyproject.toml."""
    items: List[DependencyItem] = []
    if not file_path.is_file():
        return items

    try:
        data = tomllib.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return items

    # PEP 621 [project.dependencies]
    proj_deps = data.get("project", {}).get("dependencies", [])
    for dep in proj_deps:
        m = REQ_LINE_RE.match(dep)
        if m:
            items.append(
                DependencyItem(
                    name=m.group(1).lower(),
                    version=m.group(3) or "latest",
                    ecosystem="PyPI",
                    is_direct=True,
                    scope="prod",
                    manifest_file=str(file_path),
                )
            )

    # Optional [project.optional-dependencies] (dev / test)
    opt_deps = data.get("project", {}).get("optional-dependencies", {})
    for _group, deps in opt_deps.items():
        for dep in deps:
            m = REQ_LINE_RE.match(dep)
            if m:
                items.append(
                    DependencyItem(
                        name=m.group(1).lower(),
                        version=m.group(3) or "latest",
                        ecosystem="PyPI",
                        is_direct=True,
                        scope="dev",
                        manifest_file=str(file_path),
                    )
                )

    return items

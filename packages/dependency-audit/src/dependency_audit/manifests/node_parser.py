"""Node.js dependencies parser (package.json, package-lock.json)."""

import json
from pathlib import Path
from typing import List

from dependency_audit.models import DependencyItem


def parse_package_json(file_path: Path) -> List[DependencyItem]:
    """Parse dependencies from package.json."""
    items: List[DependencyItem] = []
    if not file_path.is_file():
        return items

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return items

    prod = data.get("dependencies", {})
    for name, ver in prod.items():
        clean_ver = ver.lstrip("^~>=<")
        items.append(
            DependencyItem(
                name=name,
                version=clean_ver,
                ecosystem="npm",
                is_direct=True,
                scope="prod",
                manifest_file=str(file_path),
            )
        )

    dev = data.get("devDependencies", {})
    for name, ver in dev.items():
        clean_ver = ver.lstrip("^~>=<")
        items.append(
            DependencyItem(
                name=name,
                version=clean_ver,
                ecosystem="npm",
                is_direct=True,
                scope="dev",
                manifest_file=str(file_path),
            )
        )

    return items


def parse_package_lock_json(file_path: Path) -> List[DependencyItem]:
    """Parse locked dependencies from package-lock.json."""
    items: List[DependencyItem] = []
    if not file_path.is_file():
        return items

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return items

    # v2/v3 structure: "packages"
    packages = data.get("packages", {})
    if packages:
        for pkg_path, info in packages.items():
            if not pkg_path:  # root package
                continue
            name = info.get("name") or pkg_path.split("node_modules/")[-1]
            ver = info.get("version", "unknown")
            is_dev = info.get("dev", False)
            items.append(
                DependencyItem(
                    name=name,
                    version=ver,
                    ecosystem="npm",
                    is_direct=("node_modules/" in pkg_path and pkg_path.count("node_modules/") == 1),
                    scope="dev" if is_dev else "prod",
                    manifest_file=str(file_path),
                )
            )
    else:
        # v1 structure: "dependencies"
        deps = data.get("dependencies", {})
        for name, info in deps.items():
            items.append(
                DependencyItem(
                    name=name,
                    version=info.get("version", "unknown"),
                    ecosystem="npm",
                    is_direct=True,
                    scope="dev" if info.get("dev") else "prod",
                    manifest_file=str(file_path),
                )
            )

    return items

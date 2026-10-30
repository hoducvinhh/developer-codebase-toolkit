"""Aggregated inventory collector and duplicate detector."""

from pathlib import Path
from typing import Dict, List, Set

from dependency_audit.manifests.node_parser import parse_package_json, parse_package_lock_json
from dependency_audit.manifests.python_parser import parse_pyproject_toml, parse_requirements_txt
from dependency_audit.models import DependencyItem, InventoryResult


def collect_inventory(root_dir: str | Path) -> InventoryResult:
    """Scan root_dir for dependency manifests and aggregate items."""
    root = Path(root_dir).resolve()
    all_items: List[DependencyItem] = []

    # 1. Node manifests
    pkg_lock = root / "package-lock.json"
    if pkg_lock.is_file():
        all_items.extend(parse_package_lock_json(pkg_lock))
    else:
        pkg_json = root / "package.json"
        if pkg_json.is_file():
            all_items.extend(parse_package_json(pkg_json))

    # 2. Python manifests
    req_txt = root / "requirements.txt"
    if req_txt.is_file():
        all_items.extend(parse_requirements_txt(req_txt))

    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        all_items.extend(parse_pyproject_toml(pyproject))

    # 3. Detect duplicates (multiple distinct versions for same package)
    pkg_versions: Dict[str, Set[str]] = {}
    for item in all_items:
        if item.version and item.version not in ("latest", "unknown"):
            pkg_versions.setdefault(item.name, set()).add(item.version)

    duplicates: Dict[str, List[str]] = {
        name: sorted(list(vers))
        for name, vers in pkg_versions.items()
        if len(vers) > 1
    }

    return InventoryResult(dependencies=all_items, duplicates=duplicates)

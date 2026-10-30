"""Logical module detection in the codebase."""

from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel, Field
from toolkit_common.filesystem.walker import SafeWalker

KNOWN_ROLES = {
    "controllers": "Controller / Request Handlers",
    "routes": "API Routes / Endpoints",
    "services": "Business Logic Services",
    "models": "Data Models / Schemas",
    "views": "Presentation / Views",
    "components": "UI Components",
    "middleware": "Middleware / Interceptors",
    "utils": "Utilities & Helpers",
    "api": "API Layer",
    "cli": "Command Line Interface",
    "config": "Configuration & Settings",
}


class ModuleInfo(BaseModel):
    name: str
    path: str
    role: str = "General Module"
    file_count: int = 0
    files: List[str] = Field(default_factory=list)


def detect_modules(root_dir: str | Path) -> List[ModuleInfo]:
    """Identify logical modules and architecture boundaries."""
    root = Path(root_dir).resolve()
    walker = SafeWalker(root=root)
    files = list(walker.walk_files())

    # Map directories to files
    dir_files: Dict[Path, List[Path]] = {}
    for f in files:
        parent = f.parent
        dir_files.setdefault(parent, []).append(f)

    modules: List[ModuleInfo] = []
    seen_paths = set()

    for dir_path, dir_f in dir_files.items():
        rel = dir_path.relative_to(root) if dir_path != root else Path(".")
        dir_name = dir_path.name.lower()

        # Check for python package or js module
        has_init = any(f.name in ("__init__.py", "index.ts", "index.js", "package.json") for f in dir_f)
        role = KNOWN_ROLES.get(dir_name, "Package / Module" if has_init else None)

        if role or (has_init and str(rel) != "."):
            rel_str = str(rel).replace("\\", "/")
            if rel_str not in seen_paths:
                seen_paths.add(rel_str)
                modules.append(
                    ModuleInfo(
                        name=rel_str,
                        path=str(dir_path),
                        role=role or "Package / Module",
                        file_count=len(dir_f),
                        files=[f.name for f in dir_f],
                    )
                )

    return sorted(modules, key=lambda m: m.name)

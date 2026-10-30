"""Safe directory walker respecting .gitignore, exclusions, and symlink sandboxing."""

import os
from pathlib import Path
from typing import Iterator, List, Optional, Set

from toolkit_common.filesystem.gitignore import GitignoreMatcher

DEFAULT_EXCLUDES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".tox",
    ".idea",
    ".vscode",
    ".mypy_cache",
    ".ruff_cache",
    "coverage",
    "htmlcov",
}


class SafeWalker:
    """Safe directory traverser with depth and sandbox boundary controls."""

    def __init__(
        self,
        root: str | Path,
        respect_gitignore: bool = True,
        custom_excludes: Optional[Set[str]] = None,
        max_depth: Optional[int] = None,
        follow_symlinks: bool = False,
    ):
        self.root = Path(root).resolve()
        self.respect_gitignore = respect_gitignore
        self.custom_excludes = custom_excludes or set()
        self.max_depth = max_depth
        self.follow_symlinks = follow_symlinks

        self.gitignore_matcher: Optional[GitignoreMatcher] = None
        if self.respect_gitignore:
            gitignore_path = self.root / ".gitignore"
            if gitignore_path.exists():
                self.gitignore_matcher = GitignoreMatcher.from_file(gitignore_path)

    def is_excluded(self, path: Path, is_dir: bool = False) -> bool:
        """Check if path should be excluded based on default excludes, custom rules, or gitignore."""
        name = path.name
        if name in DEFAULT_EXCLUDES or name in self.custom_excludes:
            return True

        if self.gitignore_matcher and self.gitignore_matcher.matches(path, is_dir=is_dir):
            return True

        return False

    def is_safe_symlink(self, path: Path) -> bool:
        """Ensure symlink resolves to a target inside the root directory."""
        if not path.is_symlink():
            return True
        try:
            target = path.resolve(strict=True)
            target.relative_to(self.root)
            return True
        except (ValueError, RuntimeError, OSError):
            return False

    def walk_files(self, extensions: Optional[List[str]] = None) -> Iterator[Path]:
        """Yield all valid file Paths under root meeting criteria."""
        ext_set = {ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in extensions} if extensions else None

        for dirpath, dirnames, filenames in os.walk(str(self.root), topdown=True, followlinks=self.follow_symlinks):
            current_dir = Path(dirpath)

            # Check depth
            if self.max_depth is not None:
                try:
                    rel_parts = current_dir.relative_to(self.root).parts
                    if len(rel_parts) > self.max_depth:
                        dirnames.clear()
                        continue
                except ValueError:
                    pass

            # Prune directories in place
            filtered_dirs = []
            for d in dirnames:
                dir_full = current_dir / d
                if dir_full.is_symlink() and not self.is_safe_symlink(dir_full):
                    continue
                if not self.is_excluded(dir_full, is_dir=True):
                    filtered_dirs.append(d)
            dirnames[:] = filtered_dirs

            # Check files
            for f in filenames:
                file_full = current_dir / f
                if file_full.is_symlink() and not self.is_safe_symlink(file_full):
                    continue
                if self.is_excluded(file_full, is_dir=False):
                    continue
                if ext_set and file_full.suffix.lower() not in ext_set:
                    continue
                yield file_full

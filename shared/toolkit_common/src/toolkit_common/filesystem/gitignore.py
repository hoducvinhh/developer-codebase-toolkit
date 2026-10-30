"""Gitignore pattern matcher supporting standard gitignore syntax."""

import fnmatch
from pathlib import Path
from typing import List, Optional, Tuple


class GitignoreMatcher:
    """Matches file paths against .gitignore patterns."""

    def __init__(self, patterns: Optional[List[str]] = None, base_dir: Optional[Path] = None):
        self.base_dir = (base_dir or Path.cwd()).resolve()
        self.rules: List[Tuple[bool, str, bool]] = []  # (is_negation, pattern, is_dir_only)
        if patterns:
            for pat in patterns:
                self.add_pattern(pat)

    @classmethod
    def from_file(cls, gitignore_path: Path) -> "GitignoreMatcher":
        """Load patterns from a .gitignore file."""
        p = gitignore_path.resolve()
        matcher = cls(base_dir=p.parent)
        if p.is_file():
            try:
                content = p.read_text(encoding="utf-8", errors="replace")
                for line in content.splitlines():
                    matcher.add_pattern(line)
            except Exception:
                pass
        return matcher

    def add_pattern(self, raw_line: str) -> None:
        """Parse and add a single gitignore line."""
        line = raw_line.strip()
        if not line or line.startswith("#"):
            return

        is_negation = line.startswith("!")
        if is_negation:
            line = line[1:].strip()

        is_dir_only = line.endswith("/")
        if is_dir_only:
            line = line[:-1]

        # Normalize leading slash
        if line.startswith("/"):
            line = line[1:]

        self.rules.append((is_negation, line, is_dir_only))

    def matches(self, target_path: Path, is_dir: bool = False) -> bool:
        """Check if target_path is ignored by the loaded rules."""
        try:
            rel = target_path.resolve().relative_to(self.base_dir)
            rel_str = rel.as_posix()
        except ValueError:
            rel_str = target_path.as_posix()

        ignored = False
        for is_negation, pattern, dir_only in self.rules:
            if dir_only and not is_dir:
                continue

            # Match against full relative path or basename
            if "/" in pattern:
                match = fnmatch.fnmatch(rel_str, pattern) or fnmatch.fnmatch(rel_str, f"*/{pattern}")
            else:
                match = fnmatch.fnmatch(target_path.name, pattern) or fnmatch.fnmatch(rel_str, f"*{pattern}*")

            if match:
                ignored = not is_negation

        return ignored

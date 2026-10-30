"""Repository language and framework discovery."""

from pathlib import Path
from typing import Any, Dict, List, Set

from pydantic import BaseModel, Field
from toolkit_common.filesystem.walker import SafeWalker

EXTENSION_MAP: Dict[str, str] = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++ Header",
    ".cs": "C#",
    ".rb": "Ruby",
    ".php": "PHP",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".md": "Markdown",
    ".sql": "SQL",
    ".sh": "Shell",
}

FRAMEWORK_SIGNATURES: Dict[str, Dict[str, Any]] = {
    "FastAPI": {"manifest_keys": ["fastapi"], "file_patterns": ["fastapi"]},
    "Flask": {"manifest_keys": ["flask"], "file_patterns": ["flask"]},
    "Django": {"manifest_keys": ["django"], "file_patterns": ["django"]},
    "Express": {"manifest_keys": ["express"], "file_patterns": ["express"]},
    "Next.js": {"manifest_keys": ["next"], "file_patterns": ["next"]},
    "React": {"manifest_keys": ["react"], "file_patterns": ["react"]},
    "NestJS": {"manifest_keys": ["@nestjs/core"], "file_patterns": ["@nestjs"]},
    "Vue": {"manifest_keys": ["vue"], "file_patterns": ["vue"]},
}


class LanguageStats(BaseModel):
    files: int = 0
    lines: int = 0
    percentage: float = 0.0


class DiscoveryResult(BaseModel):
    root: str
    total_files: int = 0
    total_lines: int = 0
    languages: Dict[str, LanguageStats] = Field(default_factory=dict)
    primary_language: str = "Unknown"
    manifests: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)


def discover_repository(root_dir: str | Path) -> DiscoveryResult:
    """Analyze repository languages, lines of code, manifests, and frameworks."""
    root = Path(root_dir).resolve()
    walker = SafeWalker(root=root)

    total_files = 0
    total_lines = 0
    lang_file_counts: Dict[str, int] = {}
    lang_line_counts: Dict[str, int] = {}
    manifests: Set[str] = set()
    found_frameworks: Set[str] = set()

    manifest_names = {
        "package.json",
        "requirements.txt",
        "pyproject.toml",
        "Pipfile",
        "Cargo.toml",
        "go.mod",
        "pom.xml",
        "build.gradle",
    }

    manifest_contents: List[str] = []

    for file_path in walker.walk_files():
        total_files += 1
        name = file_path.name
        if name in manifest_names:
            manifests.add(name)
            try:
                manifest_contents.append(file_path.read_text(encoding="utf-8", errors="ignore").lower())
            except Exception:
                pass

        ext = file_path.suffix.lower()
        lang = EXTENSION_MAP.get(ext, "Other")
        lang_file_counts[lang] = lang_file_counts.get(lang, 0) + 1

        # Count lines for text files
        try:
            line_count = sum(1 for _ in open(file_path, "rb"))
            lang_line_counts[lang] = lang_line_counts.get(lang, 0) + line_count
            total_lines += line_count
        except Exception:
            pass

    # Framework detection
    combined_manifest_text = " ".join(manifest_contents)
    for framework, sig in FRAMEWORK_SIGNATURES.items():
        for key in sig["manifest_keys"]:
            if key in combined_manifest_text:
                found_frameworks.add(framework)
                break

    # Calculate percentages
    languages: Dict[str, LanguageStats] = {}
    primary_lang = "Unknown"
    max_lines = -1

    for lang, count in lang_file_counts.items():
        lines = lang_line_counts.get(lang, 0)
        pct = (lines / total_lines * 100.0) if total_lines > 0 else 0.0
        languages[lang] = LanguageStats(files=count, lines=lines, percentage=round(pct, 2))
        if lines > max_lines and lang not in ("Other", "JSON", "YAML", "Markdown"):
            max_lines = lines
            primary_lang = lang

    return DiscoveryResult(
        root=str(root),
        total_files=total_files,
        total_lines=total_lines,
        languages=languages,
        primary_language=primary_lang,
        manifests=sorted(list(manifests)),
        frameworks=sorted(list(found_frameworks)),
    )

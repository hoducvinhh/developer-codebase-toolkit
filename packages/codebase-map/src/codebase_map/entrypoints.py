"""Detection of codebase entry points and startup files."""

import json
import re
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field
from toolkit_common.filesystem.walker import SafeWalker


class EntryPoint(BaseModel):
    file: str
    kind: str  # Web App, CLI Entrypoint, Script, Worker, Library Root
    evidence: List[str] = Field(default_factory=list)
    confidence: str = "High"


def detect_entrypoints(root_dir: str | Path) -> List[EntryPoint]:
    """Scan codebase files to discover application entry points."""
    root = Path(root_dir).resolve()
    walker = SafeWalker(root=root)

    candidates: List[EntryPoint] = []

    # Check package.json for "main" or "bin"
    pkg_json = root / "package.json"
    if pkg_json.exists():
        try:
            data = json.loads(pkg_json.read_text(encoding="utf-8"))
            if "main" in data:
                candidates.append(
                    EntryPoint(
                        file=data["main"],
                        kind="NPM Main Entry",
                        evidence=["Declared as 'main' in package.json"],
                        confidence="High",
                    )
                )
            if "bin" in data:
                bin_entry = data["bin"]
                if isinstance(bin_entry, str):
                    candidates.append(
                        EntryPoint(
                            file=bin_entry,
                            kind="NPM CLI Binary",
                            evidence=["Declared as 'bin' in package.json"],
                            confidence="High",
                        )
                    )
                elif isinstance(bin_entry, dict):
                    for bname, bpath in bin_entry.items():
                        candidates.append(
                            EntryPoint(
                                file=bpath,
                                kind=f"NPM CLI Binary ({bname})",
                                evidence=[f"Declared in package.json bin.{bname}"],
                                confidence="High",
                            )
                        )
        except Exception:
            pass

    # Scan code files
    for file_path in walker.walk_files(extensions=[".py", ".js", ".ts", ".jsx", ".tsx"]):
        rel_str = str(file_path.relative_to(root)).replace("\\", "/")
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        evidence: List[str] = []
        kind = "Script Entry"

        # Python checks
        if file_path.suffix == ".py":
            if "__name__ == '__main__'" in content or '__name__ == "__main__"' in content:
                evidence.append("Contains '__name__ == \"__main__\"' guard")
            if re.search(r"FastAPI\(|Flask\(__name__\)", content):
                evidence.append("Instantiates Web Framework application (FastAPI/Flask)")
                kind = "Web Application"
            if re.search(r"@click\.command|@click\.group|typer\.Typer\(", content):
                evidence.append("Defines CLI commands via Click/Typer")
                kind = "CLI Entrypoint"
            if file_path.name in ("main.py", "app.py", "server.py", "manage.py", "cli.py"):
                evidence.append(f"Standard entry point filename: {file_path.name}")

        # JS/TS checks
        elif file_path.suffix in (".js", ".ts", ".jsx", ".tsx"):
            if re.search(r"\.listen\(\s*\d+|createServer\(", content):
                evidence.append("Contains HTTP server listen listener (.listen / createServer)")
                kind = "Web Server"
            if "#!/usr/bin/env node" in content:
                evidence.append("Contains Node shebang header")
                kind = "CLI Executable"
            if file_path.name in ("main.ts", "main.js", "server.ts", "server.js", "app.ts", "app.js", "index.ts", "index.js"):
                if str(file_path.parent) in (str(root), str(root / "src")):
                    evidence.append(f"Root/src standard entrypoint file: {file_path.name}")

        if evidence:
            candidates.append(
                EntryPoint(
                    file=rel_str,
                    kind=kind,
                    evidence=evidence,
                    confidence="High" if len(evidence) >= 2 else "Medium",
                )
            )

    # De-duplicate
    seen = set()
    deduped: List[EntryPoint] = []
    for c in candidates:
        if c.file not in seen:
            seen.add(c.file)
            deduped.append(c)

    return deduped

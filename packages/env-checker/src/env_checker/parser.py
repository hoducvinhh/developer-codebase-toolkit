"""Safe .env file parser supporting comments, quotes, multiline, and export syntax."""

import re
from pathlib import Path
from typing import Dict, Optional

from pydantic import BaseModel


class EnvEntry(BaseModel):
    key: str
    value: str
    line: int
    is_empty: bool = False
    comment: Optional[str] = None


class EnvParseResult(BaseModel):
    file_path: str
    variables: Dict[str, EnvEntry] = {}


def parse_env_file(file_path: str | Path) -> EnvParseResult:
    """Parse a .env formatted file into structured EnvEntry records."""
    p = Path(file_path).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Environment file not found: {p}")

    content = p.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    variables: Dict[str, EnvEntry] = {}
    i = 0
    total = len(lines)

    while i < total:
        raw_line = lines[i]
        line_num = i + 1
        i += 1

        stripped = raw_line.strip()
        # Skip empty lines or pure comment lines
        if not stripped or stripped.startswith("#"):
            continue

        # Handle export prefix
        if stripped.startswith("export "):
            stripped = stripped[7:].strip()

        # Parse KEY=VALUE
        if "=" in stripped:
            key, val = stripped.split("=", 1)
            key = key.strip()
            val = val.strip()

            # Handle multiline double quotes
            if val.startswith('"') and not (val.endswith('"') and len(val) > 1 and not val.endswith('\\"')):
                val_parts = [val[1:]]
                while i < total:
                    next_line = lines[i]
                    i += 1
                    if next_line.strip().endswith('"'):
                        val_parts.append(next_line.rstrip()[:-1])
                        break
                    val_parts.append(next_line)
                val = "\n".join(val_parts)
            # Handle multiline single quotes
            elif val.startswith("'") and not (val.endswith("'") and len(val) > 1 and not val.endswith("\\'")):
                val_parts = [val[1:]]
                while i < total:
                    next_line = lines[i]
                    i += 1
                    if next_line.strip().endswith("'"):
                        val_parts.append(next_line.rstrip()[:-1])
                        break
                    val_parts.append(next_line)
                val = "\n".join(val_parts)
            else:
                # Strip surrounding single or double quotes
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                else:
                    # Strip inline comments for unquoted values
                    val = re.sub(r"\s+#.*$", "", val).strip()

            variables[key] = EnvEntry(
                key=key,
                value=val,
                line=line_num,
                is_empty=(len(val) == 0),
            )
        else:
            # Key with no equals sign
            variables[stripped] = EnvEntry(
                key=stripped,
                value="",
                line=line_num,
                is_empty=True,
            )

    return EnvParseResult(file_path=str(p), variables=variables)

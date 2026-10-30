"""JavaScript and TypeScript symbol and reference extraction."""

import re
from pathlib import Path
from typing import List, Set

from dead_code_finder.symbol_table import Symbol, SymbolKind

JS_NAMED_IMPORT = re.compile(r"""import\s*\{([^}]+)\}\s*from""")
JS_DEFAULT_IMPORT = re.compile(r"""import\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s+from""")
JS_REQUIRE = re.compile(r"""(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*require\(""")

JS_FUNC_DECL = re.compile(r"""(?:export\s+)?(?:async\s+)?function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(""")
JS_CLASS_DECL = re.compile(r"""(?:export\s+)?class\s+([a-zA-Z_$][a-zA-Z0-9_$]*)""")
JS_VAR_DECL = re.compile(r"""(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=""")
JS_EXPORT_DECL = re.compile(r"""export\s+(?:const|let|var|function|class)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)""")


class JsAstAnalyzer:
    """Extracts symbols and references from JavaScript/TypeScript source."""

    def __init__(self, file_path: str | Path, content: str):
        self.file_path = str(file_path).replace("\\", "/")
        self.content = content
        self.definitions: List[Symbol] = []
        self.references: Set[str] = set()

    def analyze(self) -> None:
        lines = self.content.splitlines()

        for idx, line in enumerate(lines):
            line_no = idx + 1
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("/*"):
                continue

            # Default import
            m_def = JS_DEFAULT_IMPORT.search(line)
            if m_def:
                name = m_def.group(1)
                self.definitions.append(Symbol(name=name, kind=SymbolKind.IMPORT, file=self.file_path, line=line_no))

            # Named imports
            m_named = JS_NAMED_IMPORT.search(line)
            if m_named:
                raw_items = m_named.group(1).split(",")
                for item in raw_items:
                    parts = item.strip().split()
                    bound_name = parts[-1] if parts else ""
                    if bound_name:
                        self.definitions.append(Symbol(name=bound_name, kind=SymbolKind.IMPORT, file=self.file_path, line=line_no))

            # Require
            m_req = JS_REQUIRE.search(line)
            if m_req:
                self.definitions.append(Symbol(name=m_req.group(1), kind=SymbolKind.IMPORT, file=self.file_path, line=line_no))

            # Functions
            m_func = JS_FUNC_DECL.search(line)
            if m_func:
                name = m_func.group(1)
                is_exp = "export " in line
                self.definitions.append(Symbol(name=name, kind=SymbolKind.FUNCTION, file=self.file_path, line=line_no, is_exported=is_exp))

            # Classes
            m_class = JS_CLASS_DECL.search(line)
            if m_class:
                name = m_class.group(1)
                is_exp = "export " in line
                self.definitions.append(Symbol(name=name, kind=SymbolKind.CLASS, file=self.file_path, line=line_no, is_exported=is_exp))

            # Variables
            m_var = JS_VAR_DECL.search(line)
            if m_var:
                name = m_var.group(1)
                if not name.startswith("_"):
                    is_exp = "export " in line
                    self.definitions.append(Symbol(name=name, kind=SymbolKind.VARIABLE, file=self.file_path, line=line_no, is_exported=is_exp))

        # Collect references (words)
        all_words = set(re.findall(r"\b[a-zA-Z_$][a-zA-Z0-9_$]*\b", self.content))
        self.references.update(all_words)

"""Cross-file dead code and symbol reference analyzer."""

import re
from pathlib import Path
from typing import Dict, List, Tuple

from toolkit_common.filesystem.walker import SafeWalker
from toolkit_common.reporting.models import Confidence, Finding, Severity

from dead_code_finder.ast_javascript import JsAstAnalyzer
from dead_code_finder.ast_python import PythonAstAnalyzer
from dead_code_finder.symbol_table import Symbol, SymbolKind, SymbolTable


class DeadCodeAnalyzer:
    """Analyzes a project directory for dead/unused code."""

    def __init__(self, root_dir: str | Path, include_exports: bool = False, min_confidence: str = "low"):
        self.root = Path(root_dir).resolve()
        self.include_exports = include_exports
        self.min_confidence = min_confidence.lower()
        self.symbol_table = SymbolTable()
        self.file_symbols: Dict[str, List[Symbol]] = {}
        self.file_contents: Dict[str, str] = {}
        self.unreachable_items: List[Tuple[str, int, str]] = []  # (file, line, reason)

    def scan(self) -> List[Finding]:
        """Perform scan and return list of Finding objects."""
        walker = SafeWalker(root=self.root)
        files = list(walker.walk_files(extensions=[".py", ".js", ".ts", ".jsx", ".tsx"]))

        for f in files:
            rel_file = str(f.relative_to(self.root)).replace("\\", "/")
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            self.file_contents[rel_file] = content

            if f.suffix == ".py":
                py_analyzer = PythonAstAnalyzer(rel_file, content)
                py_analyzer.analyze()
                self.file_symbols[rel_file] = py_analyzer.definitions
                for sym in py_analyzer.definitions:
                    self.symbol_table.add_definition(sym)
                for ref in py_analyzer.references:
                    self.symbol_table.add_reference(ref, rel_file)
                for line, reason in py_analyzer.unreachable_locations:
                    self.unreachable_items.append((rel_file, line, reason))

            elif f.suffix in (".js", ".ts", ".jsx", ".tsx"):
                js_analyzer = JsAstAnalyzer(rel_file, content)
                js_analyzer.analyze()
                self.file_symbols[rel_file] = js_analyzer.definitions
                for sym in js_analyzer.definitions:
                    self.symbol_table.add_definition(sym)
                for ref in js_analyzer.references:
                    self.symbol_table.add_reference(ref, rel_file)

        findings: List[Finding] = []

        # 1. Unreachable code findings
        for rel_file, line, reason in self.unreachable_items:
            findings.append(
                Finding(
                    rule_id="DCF-UNREACHABLE-CODE",
                    severity=Severity.HIGH,
                    confidence=Confidence.HIGH,
                    file=rel_file,
                    line=line,
                    message=reason,
                    suggestion="Remove dead/unreachable code statements",
                )
            )

        # 2. Check each defined symbol
        for sym in self.symbol_table.definitions:
            content = self.file_contents.get(sym.file, "")
            lines = content.splitlines()

            # Imports: check usage within same file
            if sym.kind == SymbolKind.IMPORT:
                # Count occurrences of the symbol name outside its import definition line
                uses = 0
                for idx, line_str in enumerate(lines):
                    if idx + 1 == sym.line:
                        continue
                    if re.search(r"\b" + re.escape(sym.name) + r"\b", line_str):
                        uses += 1
                if uses == 0:
                    findings.append(
                        Finding(
                            rule_id="DCF-UNUSED-IMPORT",
                            severity=Severity.MEDIUM,
                            confidence=Confidence.HIGH,
                            file=sym.file,
                            line=sym.line,
                            column=sym.col,
                            symbol=sym.name,
                            message=f"Import '{sym.name}' is never used in {sym.file}",
                            suggestion=f"Remove unused import '{sym.name}'",
                        )
                    )

            # Variables: check usage within same file
            elif sym.kind == SymbolKind.VARIABLE:
                uses = 0
                for idx, line_str in enumerate(lines):
                    if idx + 1 == sym.line:
                        continue
                    if re.search(r"\b" + re.escape(sym.name) + r"\b", line_str):
                        uses += 1
                if uses == 0:
                    findings.append(
                        Finding(
                            rule_id="DCF-UNUSED-VARIABLE",
                            severity=Severity.LOW,
                            confidence=Confidence.HIGH,
                            file=sym.file,
                            line=sym.line,
                            column=sym.col,
                            symbol=sym.name,
                            message=f"Variable '{sym.name}' is assigned but never read",
                            suggestion=f"Remove unused variable '{sym.name}' or prefix with '_'",
                        )
                    )

            # Functions and classes
            elif sym.kind in (SymbolKind.FUNCTION, SymbolKind.CLASS):
                # Ignore test functions or standard entrypoints
                if sym.name.startswith("test_") or sym.name in ("main", "setUp", "tearDown"):
                    continue
                # Ignore functions with framework decorators (e.g. FastAPI routes, pytest fixtures)
                if sym.decorators:
                    continue

                # If private, check same file
                if sym.is_private:
                    uses = 0
                    for idx, line_str in enumerate(lines):
                        if idx + 1 == sym.line:
                            continue
                        if re.search(r"\b" + re.escape(sym.name) + r"\b", line_str):
                            uses += 1
                    if uses == 0:
                        findings.append(
                            Finding(
                                rule_id="DCF-UNUSED-PRIVATE-FUNCTION" if sym.kind == SymbolKind.FUNCTION else "DCF-UNUSED-PRIVATE-CLASS",
                                severity=Severity.MEDIUM,
                                confidence=Confidence.MEDIUM,
                                file=sym.file,
                                line=sym.line,
                                column=sym.col,
                                symbol=sym.name,
                                message=f"Private {sym.kind.value} '{sym.name}' is defined but never called in {sym.file}",
                                suggestion=f"Review and remove dead {sym.kind.value} '{sym.name}'",
                            )
                        )
                else:
                    # Public symbol: check if referenced globally across all files
                    global_uses = 0
                    for file_p, f_content in self.file_contents.items():
                        for idx, line_str in enumerate(f_content.splitlines()):
                            if file_p == sym.file and idx + 1 == sym.line:
                                continue
                            if re.search(r"\b" + re.escape(sym.name) + r"\b", line_str):
                                global_uses += 1
                    if global_uses == 0:
                        # If include_exports is off, mark Low confidence because it could be public API
                        findings.append(
                            Finding(
                                rule_id=f"DCF-UNUSED-{sym.kind.value.upper()}",
                                severity=Severity.LOW,
                                confidence=Confidence.MEDIUM if not sym.is_exported else Confidence.LOW,
                                file=sym.file,
                                line=sym.line,
                                column=sym.col,
                                symbol=sym.name,
                                message=f"{sym.kind.value.capitalize()} '{sym.name}' has no references across scanned files",
                                suggestion=f"Check if '{sym.name}' is intended as public API or can be safely removed",
                            )
                        )

        # Filter by min_confidence
        conf_ranks = {"low": 1, "medium": 2, "high": 3}
        min_rank = conf_ranks.get(self.min_confidence, 1)
        filtered = [f for f in findings if conf_ranks.get(f.confidence.value, 1) >= min_rank]

        return filtered

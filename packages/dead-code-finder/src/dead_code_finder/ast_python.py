"""Python AST analysis for symbol collection and unreachable code detection."""

import ast
from pathlib import Path
from typing import List, Set, Tuple

from dead_code_finder.symbol_table import Symbol, SymbolKind


class PythonAstAnalyzer:
    """Extracts symbols, references, and unreachable code from Python AST."""

    def __init__(self, file_path: str | Path, content: str):
        self.file_path = str(file_path).replace("\\", "/")
        self.content = content
        self.definitions: List[Symbol] = []
        self.references: Set[str] = set()
        self.unreachable_locations: List[Tuple[int, str]] = []  # (line, reason)

    def analyze(self) -> None:
        try:
            tree = ast.parse(self.content)
        except SyntaxError:
            return

        self._collect_symbols_and_references(tree)
        self._detect_unreachable(tree)

    def _collect_symbols_and_references(self, tree: ast.AST) -> None:
        for node in ast.walk(tree):
            # Imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    bound_name = alias.asname or alias.name.split(".")[0]
                    self.definitions.append(
                        Symbol(
                            name=bound_name,
                            kind=SymbolKind.IMPORT,
                            file=self.file_path,
                            line=node.lineno,
                            col=node.col_offset,
                        )
                    )
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    bound_name = alias.asname or alias.name
                    if bound_name != "*":
                        self.definitions.append(
                            Symbol(
                                name=bound_name,
                                kind=SymbolKind.IMPORT,
                                file=self.file_path,
                                line=node.lineno,
                                col=node.col_offset,
                            )
                        )

            # Function definitions
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                decorators = []
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Name):
                        decorators.append(dec.id)
                    elif isinstance(dec, ast.Attribute):
                        decorators.append(dec.attr)
                    elif isinstance(dec, ast.Call):
                        if isinstance(dec.func, ast.Name):
                            decorators.append(dec.func.id)
                        elif isinstance(dec.func, ast.Attribute):
                            decorators.append(dec.func.attr)

                is_priv = node.name.startswith("_") and not node.name.startswith("__")
                self.definitions.append(
                    Symbol(
                        name=node.name,
                        kind=SymbolKind.FUNCTION,
                        file=self.file_path,
                        line=node.lineno,
                        col=node.col_offset,
                        is_private=is_priv,
                        decorators=decorators,
                    )
                )

            # Class definitions
            elif isinstance(node, ast.ClassDef):
                is_priv = node.name.startswith("_") and not node.name.startswith("__")
                self.definitions.append(
                    Symbol(
                        name=node.name,
                        kind=SymbolKind.CLASS,
                        file=self.file_path,
                        line=node.lineno,
                        col=node.col_offset,
                        is_private=is_priv,
                    )
                )

            # Variable assignments (module / top-level or class body)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        vname = target.id
                        # Check __all__
                        if vname == "__all__" and isinstance(node.value, (ast.List, ast.Tuple)):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    self.references.add(elt.value)
                        elif not vname.startswith("_"):
                            self.definitions.append(
                                Symbol(
                                    name=vname,
                                    kind=SymbolKind.VARIABLE,
                                    file=self.file_path,
                                    line=node.lineno,
                                    col=node.col_offset,
                                )
                            )

            # Reference lookups
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                self.references.add(node.id)

    def _detect_unreachable(self, tree: ast.AST) -> None:
        """Find statements located after return, raise, break, or continue in any block."""
        for node in ast.walk(tree):
            for body_attr in ("body", "orelse", "finalbody"):
                stmt_list = getattr(node, body_attr, None)
                if isinstance(stmt_list, list) and len(stmt_list) > 1:
                    terminal_found = False
                    term_type = ""
                    for stmt in stmt_list:
                        if terminal_found:
                            self.unreachable_locations.append(
                                (stmt.lineno, f"Unreachable statement after '{term_type}'")
                            )
                        elif isinstance(stmt, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                            terminal_found = True
                            term_type = type(stmt).__name__.lower()

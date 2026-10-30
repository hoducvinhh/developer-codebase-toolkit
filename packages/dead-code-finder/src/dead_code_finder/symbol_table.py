"""Symbol definitions and cross-reference records."""

from enum import Enum
from typing import Dict, List, Set

from pydantic import BaseModel, Field


class SymbolKind(str, Enum):
    IMPORT = "import"
    VARIABLE = "variable"
    FUNCTION = "function"
    METHOD = "method"
    CLASS = "class"
    EXPORT = "export"


class Symbol(BaseModel):
    name: str
    kind: SymbolKind
    file: str
    line: int
    col: int = 1
    is_exported: bool = False
    is_private: bool = False
    decorators: List[str] = Field(default_factory=list)


class SymbolTable(BaseModel):
    definitions: List[Symbol] = Field(default_factory=list)
    references: Set[str] = Field(default_factory=set)
    file_references: Dict[str, Set[str]] = Field(default_factory=dict)

    def add_definition(self, sym: Symbol) -> None:
        self.definitions.append(sym)

    def add_reference(self, name: str, file_path: str) -> None:
        self.references.add(name)
        self.file_references.setdefault(file_path, set()).add(name)

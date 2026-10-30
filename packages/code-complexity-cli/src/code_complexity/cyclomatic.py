"""Cyclomatic complexity measurement (McCabe)."""

import ast
import re
from typing import Union

JS_BRANCH_RE = re.compile(
    r"\b(?:if|for|while|catch|case)\b|&&|\|\||\?[^:\n]+:"
)


def calculate_python_cyclomatic(node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> int:
    """Calculate cyclomatic complexity of a Python function AST node."""
    complexity = 1  # Base complexity

    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.For, ast.AsyncFor, ast.While)):
            complexity += 1
        elif isinstance(child, ast.ExceptHandler):
            complexity += 1
        elif isinstance(child, (ast.With, ast.AsyncWith)):
            complexity += 1
        elif isinstance(child, ast.Assert):
            complexity += 1
        elif isinstance(child, ast.IfExp):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            # len(values) - 1 additional branches
            complexity += max(0, len(child.values) - 1)
        elif hasattr(ast, "MatchCase") and isinstance(child, ast.MatchCase):
            complexity += 1

    return complexity


def calculate_js_cyclomatic(code_snippet: str) -> int:
    """Estimate cyclomatic complexity for JavaScript / TypeScript snippet."""
    matches = JS_BRANCH_RE.findall(code_snippet)
    return 1 + len(matches)

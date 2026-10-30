"""Cognitive complexity measurement (SonarQube specification)."""

import ast
from typing import Union


class CognitiveComplexityVisitor(ast.NodeVisitor):
    """AST Visitor that calculates Cognitive Complexity with nesting penalties."""

    def __init__(self, func_name: str):
        self.func_name = func_name
        self.complexity = 0
        self.nesting_level = 0
        self.max_nesting = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.name == self.func_name:
            # Entering root function: do not penalize function definition itself
            self.generic_visit(node)
        else:
            # Nested function
            self.complexity += 1 + self.nesting_level
            self.nesting_level += 1
            self.max_nesting = max(self.max_nesting, self.nesting_level)
            self.generic_visit(node)
            self.nesting_level -= 1

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_If(self, node: ast.If) -> None:
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)

        # Visit body
        for stmt in node.body:
            self.visit(stmt)

        # Check else/elif
        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                # elif: do not increase nesting level, but add +1 complexity
                self.complexity += 1
                self.visit(node.orelse[0].test)
                for s in node.orelse[0].body:
                    self.visit(s)
                # Recurse orelse
                if node.orelse[0].orelse:
                    self.visit(ast.If(test=ast.Constant(value=True), body=node.orelse[0].orelse, orelse=[]))
            else:
                # else: add +1 complexity
                self.complexity += 1
                for stmt in node.orelse:
                    self.visit(stmt)

        self.nesting_level -= 1

    def visit_For(self, node: ast.For) -> None:
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1

    visit_AsyncFor = visit_For

    def visit_While(self, node: ast.While) -> None:
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        # Each boolean sequence increments complexity by 1
        self.complexity += 1
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        # Detect direct recursion
        if isinstance(node.func, ast.Name) and node.func.id == self.func_name:
            self.complexity += 1
        self.generic_visit(node)


def calculate_python_cognitive(node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> int:
    """Calculate Cognitive Complexity for a Python function."""
    visitor = CognitiveComplexityVisitor(func_name=node.name)
    visitor.visit(node)
    return visitor.complexity


def calculate_max_nesting(node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> int:
    """Calculate maximum nesting depth in function."""
    visitor = CognitiveComplexityVisitor(func_name=node.name)
    visitor.visit(node)
    return visitor.max_nesting

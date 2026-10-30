"""Complexity analysis, ranking, and hotspot identification."""

import ast
from pathlib import Path
from typing import List

from toolkit_common.reporting.models import Confidence, Finding, Severity

from code_complexity.cognitive import calculate_max_nesting, calculate_python_cognitive
from code_complexity.cyclomatic import calculate_python_cyclomatic
from code_complexity.metrics import ClassMetrics, ComplexityThresholds, FileMetrics, FunctionMetrics


def analyze_python_file(path: Path) -> FileMetrics:
    """Analyze a single Python file and extract function, class, and file metrics."""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)
    except Exception:
        return FileMetrics(file=str(path))

    lines = content.splitlines()
    total_loc = len(lines)
    functions: List[FunctionMetrics] = []
    classes: List[ClassMetrics] = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            m = _measure_function(node, path, lines)
            functions.append(m)
        elif isinstance(node, ast.ClassDef):
            c = _measure_class(node, path, lines)
            classes.append(c)
            # Add methods to functions list as well
            functions.extend(c.methods)

    tot_cyc = sum(f.cyclomatic_complexity for f in functions)
    tot_cog = sum(f.cognitive_complexity for f in functions)

    return FileMetrics(
        file=str(path).replace("\\", "/"),
        loc=total_loc,
        functions=functions,
        classes=classes,
        total_cyclomatic=tot_cyc,
        total_cognitive=tot_cog,
    )


def _measure_function(node: ast.FunctionDef, path: Path, lines: List[str]) -> FunctionMetrics:
    start_line = node.lineno
    end_line = getattr(node, "end_lineno", start_line)
    loc = max(1, end_line - start_line + 1)

    # Count parameters (posonlyargs, args, kwonlyargs, vararg, kwarg)
    param_count = len(node.args.args) + len(node.args.kwonlyargs) + len(getattr(node.args, "posonlyargs", []))
    if node.args.vararg:
        param_count += 1
    if node.args.kwarg:
        param_count += 1

    # Logical lines: statements inside body
    lloc = sum(1 for _ in ast.walk(node) if isinstance(_, ast.stmt))

    cyc = calculate_python_cyclomatic(node)
    cog = calculate_python_cognitive(node)
    max_nest = calculate_max_nesting(node)

    return FunctionMetrics(
        name=node.name,
        file=str(path).replace("\\", "/"),
        start_line=start_line,
        end_line=end_line,
        loc=loc,
        lloc=lloc,
        parameter_count=param_count,
        max_nesting_depth=max_nest,
        cyclomatic_complexity=cyc,
        cognitive_complexity=cog,
    )


def _measure_class(node: ast.ClassDef, path: Path, lines: List[str]) -> ClassMetrics:
    start_line = node.lineno
    end_line = getattr(node, "end_lineno", start_line)
    loc = max(1, end_line - start_line + 1)

    methods: List[FunctionMetrics] = []
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods.append(_measure_function(item, path, lines))

    avg_cyc = (sum(m.cyclomatic_complexity for m in methods) / len(methods)) if methods else 1.0

    return ClassMetrics(
        name=node.name,
        file=str(path).replace("\\", "/"),
        start_line=start_line,
        end_line=end_line,
        loc=loc,
        methods=methods,
        avg_cyclomatic=round(avg_cyc, 2),
    )


def rank_hotspots(all_functions: List[FunctionMetrics], top_n: int = 10) -> List[FunctionMetrics]:
    """Rank functions by combined complexity and maintainability penalty score."""
    def score(f: FunctionMetrics) -> float:
        return f.cyclomatic_complexity * 1.5 + f.cognitive_complexity * 2.0 + f.loc * 0.1

    return sorted(all_functions, key=score, reverse=True)[:top_n]


def generate_threshold_findings(all_functions: List[FunctionMetrics], thresholds: ComplexityThresholds) -> List[Finding]:
    """Check functions against thresholds and produce actionable findings."""
    findings: List[Finding] = []

    for f in all_functions:
        if f.cyclomatic_complexity > thresholds.max_cyclomatic:
            findings.append(
                Finding(
                    rule_id="CCX-CYCLOMATIC-EXCEEDED",
                    severity=Severity.HIGH,
                    confidence=Confidence.HIGH,
                    file=f.file,
                    line=f.start_line,
                    symbol=f.name,
                    message=f"Function '{f.name}' has Cyclomatic Complexity of {f.cyclomatic_complexity} (max allowed: {thresholds.max_cyclomatic})",
                    suggestion="Refactor complex conditional branches into smaller helper functions",
                )
            )

        if f.cognitive_complexity > thresholds.max_cognitive:
            findings.append(
                Finding(
                    rule_id="CCX-COGNITIVE-EXCEEDED",
                    severity=Severity.HIGH,
                    confidence=Confidence.HIGH,
                    file=f.file,
                    line=f.start_line,
                    symbol=f.name,
                    message=f"Function '{f.name}' has Cognitive Complexity of {f.cognitive_complexity} (max allowed: {thresholds.max_cognitive})",
                    suggestion="Flatten nested if/loop structures and break up control flow",
                )
            )

        if f.loc > thresholds.max_loc:
            findings.append(
                Finding(
                    rule_id="CCX-FUNCTION-TOO-LONG",
                    severity=Severity.MEDIUM,
                    confidence=Confidence.HIGH,
                    file=f.file,
                    line=f.start_line,
                    symbol=f.name,
                    message=f"Function '{f.name}' has {f.loc} lines of code (max recommended: {thresholds.max_loc})",
                    suggestion="Extract blocks of logic into focused helper functions",
                )
            )

        if f.parameter_count > thresholds.max_parameters:
            findings.append(
                Finding(
                    rule_id="CCX-TOO-MANY-PARAMETERS",
                    severity=Severity.MEDIUM,
                    confidence=Confidence.HIGH,
                    file=f.file,
                    line=f.start_line,
                    symbol=f.name,
                    message=f"Function '{f.name}' takes {f.parameter_count} parameters (max recommended: {thresholds.max_parameters})",
                    suggestion="Group related parameters into a parameter object or dataclass",
                )
            )

    return findings

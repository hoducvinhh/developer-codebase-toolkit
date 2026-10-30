"""Data models for complexity measurements and threshold configuration."""

from typing import List

from pydantic import BaseModel, Field


class FunctionMetrics(BaseModel):
    name: str
    file: str
    start_line: int
    end_line: int
    loc: int
    lloc: int = 0
    parameter_count: int = 0
    max_nesting_depth: int = 0
    cyclomatic_complexity: int = 1
    cognitive_complexity: int = 0


class ClassMetrics(BaseModel):
    name: str
    file: str
    start_line: int
    end_line: int
    loc: int
    methods: List[FunctionMetrics] = Field(default_factory=list)
    avg_cyclomatic: float = 1.0


class FileMetrics(BaseModel):
    file: str
    loc: int = 0
    functions: List[FunctionMetrics] = Field(default_factory=list)
    classes: List[ClassMetrics] = Field(default_factory=list)
    total_cyclomatic: int = 0
    total_cognitive: int = 0


class ComplexityThresholds(BaseModel):
    max_cyclomatic: int = 10
    max_cognitive: int = 15
    max_loc: int = 50
    max_parameters: int = 5
    max_nesting_depth: int = 4

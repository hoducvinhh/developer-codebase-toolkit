# code-complexity-cli (`ccx`)

Measure Cyclomatic Complexity, Cognitive Complexity, LOC, and identify maintainability hotspots.

## Installation
```bash
pip install -e packages/code-complexity-cli
```

## Usage
```bash
# Full complexity report
ccx report .

# Top maintainability hotspots
ccx hotspots . --top 10

# Single file in-depth analysis
ccx analyze src/main.py
```

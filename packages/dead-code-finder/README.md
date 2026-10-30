# dead-code-finder (`dcf`)

Detect unused imports, variables, functions, classes, and dead code across Python and JavaScript / TypeScript codebases.

## Installation
```bash
pip install -e packages/dead-code-finder
```

## Usage
```bash
# Scan directory for dead code
dcf scan .

# Filter by minimum confidence (high, medium, low)
dcf scan . --min-confidence high

# Include public export checks
dcf scan . --include-exports
```

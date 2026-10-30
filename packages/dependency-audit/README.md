# dependency-audit (`da`)

Audit project dependencies for security vulnerabilities (via OSV database), outdated packages, duplicate versions, and license compliance.

## Installation
```bash
pip install -e packages/dependency-audit
```

## Usage
```bash
# Full dependency audit
da scan .

# Vulnerability lookup (supports --offline cache)
da audit . --offline

# Outdated dependency version distance
da outdated .

# License compliance check
da licenses . --policy permissive
```

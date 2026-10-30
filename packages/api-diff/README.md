# api-diff

A CLI tool to compare OpenAPI 3.0 and 3.1 specifications and detect breaking changes.

## Installation
```bash
pip install -e packages/api-diff
```

## Usage
```bash
# Compare old and new OpenAPI spec
api-diff old-spec.json new-spec.yaml

# Fail CI/CD build if breaking changes exist
api-diff old-spec.json new-spec.json --fail-on breaking
```

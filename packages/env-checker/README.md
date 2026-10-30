# env-checker (`envcheck`)

A security-first CLI tool for environment configuration validation, template auditing, schema verification, and secret exposure prevention.

## Installation
```bash
pip install -e packages/env-checker
```

## Usage
```bash
# Full audit
envcheck .

# Compare template with actual env
envcheck compare .env.example .env

# Validate types and constraints against schema
envcheck validate .env --schema envcheck.yml

# Scan source code for environment variable usages
envcheck analyze-usage .

# Check for committed secret values
envcheck secrets .
```

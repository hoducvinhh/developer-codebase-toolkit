# Contributing to Developer Code Quality & Analysis Toolkit

Thank you for your interest in contributing to `developer-code-toolkit`!

## Monorepo Layout

- `shared/toolkit_common`: Shared foundational library (CLI options, exit codes, Pydantic report models, formatters, SafeWalker, SecretRedactor).
- `packages/codebase-map`: `cbm` CLI.
- `packages/dead-code-finder`: `dcf` CLI.
- `packages/dependency-audit`: `da` CLI.
- `packages/code-complexity-cli`: `ccx` CLI.
- `packages/env-checker`: `envcheck` CLI.
- `packages/api-diff`: `api-diff` CLI.

## Development Setup

1. Install requirements and development tools:
   ```bash
   pip install -e shared/toolkit_common
   pip install -e packages/codebase-map
   pip install -e packages/env-checker
   pip install -e packages/api-diff
   pip install -e packages/dead-code-finder
   pip install -e packages/code-complexity-cli
   pip install -e packages/dependency-audit
   ```
2. Run test suites:
   ```bash
   pytest
   ```
3. Run linting:
   ```bash
   ruff check .
   ```

## Guidelines

- All CLI tools must maintain standalone `pyproject.toml` configurations.
- Adhere to the standardized exit codes:
  - 0: Success / clean
  - 1: Blocking findings
  - 2: Invalid arguments or configuration
  - 3: Runtime error
  - 4: Unsupported format or target
- Never leak sensitive secrets in CLI outputs or test logs. Always use `SecretRedactor`.

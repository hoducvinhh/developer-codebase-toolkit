# Architecture & Design Overview

The `developer-code-toolkit` is organized as an independent-lifecycle monorepo.

## 1. Monorepo Principles
1. **Zero Coupled Lifecycles:** Each package in `packages/` is completely standalone with its own `pyproject.toml`.
2. **Lightweight Shared Core (`shared/toolkit_common`):** Provides cross-cutting primitives:
   - `toolkit_common.cli`: Exit code standard (0-4), click option decorators.
   - `toolkit_common.reporting`: Unified Pydantic models (`Finding`, `Summary`, `Report`) and formatters (Terminal, JSON, Markdown, SARIF v2.1.0).
   - `toolkit_common.filesystem`: `SafeWalker` with symlink sandbox containment and `.gitignore` integration.
   - `toolkit_common.secrets`: `SecretRedactor` with Shannon entropy detection and regex masking.
3. **Strict Read-Only Guarantee:** None of the analysis tools automatically rewrite user source code, preventing unintended data loss.

## 2. Package Dependency Graph

```text
[ toolkit_common ]
       ▲
       │ (depends on)
   ┌───┴───────────────────────────────────────────────┐
   │         │          │           │         │        │
 [ cbm ] [ envcheck ] [ api-diff ] [ dcf ] [ ccx ]  [ da ]
```

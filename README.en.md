# Developer Code Quality & Analysis Toolkit (`developer-code-toolkit`)

<div align="center">

**An open-source collection of developer CLI tools for analyzing codebases, detecting dead code, auditing dependencies, measuring complexity, validating environment configurations, and catching API breaking changes.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Tests: Pytest](https://img.shields.io/badge/Tests-36%20Passed-brightgreen.svg)](#-testing)

[🇻🇳 Tiếng Việt](README.md) | [🇬🇧 English](README.en.md)

</div>

---

## 📑 Table of Contents
1. [Overview](#-overview)
2. [Monorepo Architecture & Included Tools](#-monorepo-architecture--included-tools)
3. [Installation](#-installation)
4. [Common Options & Standard Exit Codes](#-common-options--standard-exit-codes)
5. [Detailed Tool Reference Manual](#-detailed-tool-reference-manual)
   - [1. `cbm` — Codebase Map](#1-cbm--codebase-map)
   - [2. `envcheck` — Environment Checker](#2-envcheck--environment-checker)
   - [3. `api-diff` — API Diff](#3-api-diff--api-diff)
   - [4. `dcf` — Dead Code Finder](#4-dcf--dead-code-finder)
   - [5. `ccx` — Code Complexity CLI](#5-ccx--code-complexity-cli)
   - [6. `da` — Dependency Audit](#6-da--dependency-audit)
6. [Reporting Formats](#-reporting-formats)
7. [Configuration File Examples](#-configuration-file-examples)
8. [CI/CD Pipeline Integration (GitHub Actions)](#-cicd-pipeline-integration-github-actions)
9. [Testing](#-testing)
10. [License](#-license)

---

## 🌟 Overview

Modern software engineering frequently encounters recurrent code quality and maintenance friction:
- Large or unfamiliar repositories are difficult to onboard and map.
- Dead code, unused imports, and orphaned variables accumulate silently.
- Environment variables (`.env`) drift across team members, and secrets are accidentally committed.
- API changes inadvertently introduce breaking contracts to clients and frontend apps.
- Functions grow excessively complex, hindering readability, unit testing, and maintainability.
- Dependencies introduce known Common Vulnerabilities and Exposures (CVEs) or restrictive copyleft licenses.

**`developer-code-toolkit`** resolves these challenges through **6 specialized, standalone CLI utilities** adhering to strict safety (**Read-Only by default**) and out-of-the-box CI/CD readiness.

---

## 🛠️ Monorepo Architecture & Included Tools

The repository utilizes an independent **Zero-Coupled Monorepo** design. Each package in [`packages/`](packages/) maintains its own isolated lifecycle and `pyproject.toml`. The [`shared/toolkit_common`](shared/toolkit_common) library provides unified reporting formatters, exit codes, path-safe walking, and secret redaction.

| Tool | CLI Command | Package Path | Primary Responsibility |
| :--- | :--- | :--- | :--- |
| **Codebase Map** | `cbm` | [`packages/codebase-map`](packages/codebase-map) | Visualizes repo structure, entry points, language/framework detection, and Mermaid flowcharts. |
| **Environment Checker** | `envcheck` | [`packages/env-checker`](packages/env-checker) | Compares `.env` against templates, validates types via schema, audits code usage, and flags secrets. |
| **API Diff** | `api-diff` | [`packages/api-diff`](packages/api-diff) | Compares OpenAPI 3.0/3.1 specs (JSON/YAML) and detects breaking changes before release. |
| **Dead Code Finder** | `dcf` | [`packages/dead-code-finder`](packages/dead-code-finder) | AST-based detection of unused imports, unreferenced variables, dead functions, and unreachable code. |
| **Code Complexity CLI** | `ccx` | [`packages/code-complexity-cli`](packages/code-complexity-cli) | Measures Cyclomatic and Cognitive complexity, nesting depth, and ranks maintainability hotspots. |
| **Dependency Audit** | `da` | [`packages/dependency-audit`](packages/dependency-audit) | Scans manifests for known CVEs (OSV database), version duplication, and license risk. |

---

## 🚀 Installation

### Prerequisites
- **Python:** `>= 3.10` (compatible with Python 3.10, 3.11, 3.12, 3.13, 3.14).
- **Package Manager:** `pip`.

### 1. Install All Tools (Recommended)

```bash
git clone https://github.com/hoducvinhh/developer-codebase-toolkit.git
cd developer-codebase-toolkit

# 1. Install shared common foundation (required)
pip install -e shared/toolkit_common

# 2. Install CLI packages in editable mode
pip install -e packages/codebase-map
pip install -e packages/env-checker
pip install -e packages/api-diff
pip install -e packages/dead-code-finder
pip install -e packages/code-complexity-cli
pip install -e packages/dependency-audit
```

### 2. Standalone Package Installation

Install only the tools relevant to your workflow:

```bash
pip install -e shared/toolkit_common
pip install -e packages/codebase-map
pip install -e packages/code-complexity-cli
```

### 3. Verify Installation

```bash
cbm --version
envcheck --version
api-diff --help
dcf --version
ccx --version
da --version
```

---

## ⚙️ Common Options & Standard Exit Codes

### 1. Standardized CLI Flags

| Flag | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `-f, --format` | `-f` | `terminal` | Output format: `terminal`, `json`, `markdown`, `sarif`. |
| `-o, --output` | `-o` | *(stdout)* | Write report directly to target file path. |
| `-c, --config` | `-c` | *(auto)* | Specify custom config file (`.yml` / `.toml` / `.json`). |
| `-q, --quiet` | `-q` | `false` | Quiet mode: suppress informational messages, emit findings only. |
| `-v, --verbose` | `-v` | `false` | Verbose debug mode: print full stack traces on error. |
| `--no-color` | | `false` | Disable ANSI color sequences. |

### 2. Exit Code Standard

| Exit Code | Name | Semantic Meaning |
| :---: | :--- | :--- |
| **0** | `SUCCESS` | Clean execution; no blocking findings identified. |
| **1** | `BLOCKING_FINDINGS` | Violations or breaking changes exceeded configured threshold. |
| **2** | `INVALID_CONFIG` | Bad arguments or malformed configuration schema. |
| **3** | `RUNTIME_ERROR` | An unhandled exception or parsing failure occurred. |
| **4** | `UNSUPPORTED` | Input format or ecosystem is unsupported. |

---

## 📖 Detailed Tool Reference Manual

---

### 1. `cbm` — Codebase Map

#### `cbm analyze [DIRECTORY]`
Scans the repository to identify primary programming languages, frameworks, entry points, module breakdown, and total line counts.

```bash
cbm analyze .
cbm analyze /path/to/project -f json -o analysis.json
```

#### `cbm tree [DIRECTORY]`
Renders a structured directory tree with file statistics.
- `-d, --depth INTEGER`: Maximum nesting depth (default: `3`).

```bash
cbm tree . --depth 2
cbm tree . --depth 3 -f json -o tree.json
```

#### `cbm deps [DIRECTORY]`
Summarizes internal inter-module imports and third-party dependencies.

```bash
cbm deps .
```

#### `cbm diagram [DIRECTORY]`
Generates an architecture **Mermaid flowchart**.
- `--direction [TD|LR]`: Layout orientation (`TD`: Top-Down, `LR`: Left-Right. Default: `TD`).
- `-o, --output PATH`: Save flowchart to file.

```bash
cbm diagram .
cbm diagram . --direction LR -o docs/architecture.mmd
```

---

### 2. `envcheck` — Environment Checker

#### `envcheck [DIRECTORY]` *(Default Command)*
Executes full environment audit: compares `.env` with `.env.example`, validates schema, and scans for secrets.
- `--fail-on [missing|secret|schema|any]`: Condition triggering exit code 1 (default: `missing`).

```bash
envcheck .
envcheck . --fail-on any
```

#### `envcheck compare <TEMPLATE> <TARGET>`
Diffs a template against a target file to catch `ENV-MISSING` and `ENV-EXTRA` keys.

```bash
envcheck compare .env.example .env
```

#### `envcheck validate <ENV_FILE> --schema <SCHEMA_FILE>`
Validates environment variable types and bounds against a schema file.
- `-s, --schema PATH`: Path to `envcheck.yml` schema (required).

```bash
envcheck validate .env --schema envcheck.yml
```

#### `envcheck analyze-usage [DIRECTORY]`
Scans code (`process.env`, `os.environ`, `os.getenv`) and cross-checks with `.env.example` to detect undocumented variables.
- `-t, --template PATH`: Template file path (default: `.env.example`).

```bash
envcheck analyze-usage .
```

#### `envcheck secrets [DIRECTORY]`
Scans environment files and repository for unmasked plaintext secret tokens using Shannon Entropy and regex heuristics.

```bash
envcheck secrets .
```

---

### 3. `api-diff` — API Diff

#### `api-diff <OLD_SPEC> <NEW_SPEC> [OPTIONS]`
Compares two OpenAPI 3.0/3.1 specs (JSON/YAML) and categorizes changes into Breaking, Potentially Breaking, and Non-breaking.

- `--fail-on [breaking|potentially_breaking|none]`: Level that triggers exit code 1 (default: `breaking`).
- `-f, --format [terminal|json|markdown|sarif]`: Output style.
- `-o, --output PATH`: Destination file.

```bash
api-diff openapi-v1.json openapi-v2.json
api-diff openapi-v1.yaml openapi-v2.yaml --fail-on breaking -f markdown -o pr-diff.md
```

---

### 4. `dcf` — Dead Code Finder

#### `dcf scan [DIRECTORY] [OPTIONS]`
Scans Python & JavaScript/TypeScript ASTs for unused imports, unused variables, dead functions, and unreachable code.

- `--min-confidence [low|medium|high]`: Minimum confidence threshold (default: `low`).
- `--include-exports`: Also flag unused public export symbols.
- `--fail-on-findings`: Exit with code 1 if dead code is found.

```bash
dcf scan .
dcf scan . --min-confidence high
dcf scan src/ --include-exports --fail-on-findings
```

---

### 5. `ccx` — Code Complexity CLI

Measures Cyclomatic Complexity (McCabe) and Cognitive Complexity (Sonar).

#### `ccx report [DIRECTORY]`
Scans all source files against configured threshold limits.
- `--fail-on-threshold`: Exit with code 1 if any function exceeds limits.
- `-c, --config PATH`: Configuration file path (default: `ccx.yml`).

```bash
ccx report .
ccx report . --fail-on-threshold
```

#### `ccx hotspots [DIRECTORY]`
Ranks top maintainability hotspots.
- `-n, --top INTEGER`: Number of top hotspots to list (default: `10`).

```bash
ccx hotspots . --top 5
ccx hotspots . -n 10 -f json -o hotspots.json
```

#### `ccx analyze <FILE_PATH>`
Analyzes function-by-function complexity metrics for a single file.

```bash
ccx analyze packages/codebase-map/src/codebase_map/dependencies.py
```

---

### 6. `da` — Dependency Audit

Audits package dependencies, CVE vulnerabilities, version duplications, and licenses.

#### `da scan [DIRECTORY]`
Runs full dependency audit:
1. **Duplicate packages (`DA-DUPLICATE-DEPENDENCY`)**: Multiple versions of the same package.
2. **License violations (`DA-LICENSE-VIOLATION`)**: Copyleft or restrictive licenses.
3. **Vulnerabilities (`DA-VULN-*`)**: Querying the Open Source Vulnerabilities (**OSV**) database.

- `--policy [permissive|copyleft]`: License compliance policy (default: `permissive`).
- `--offline`: Use cached vulnerability data only (`.osv_cache.json`).
- `--fail-on-vuln`: Exit with code 1 if any vulnerability is found.

```bash
da scan .
da scan . --policy copyleft
da scan . --fail-on-vuln
```

#### `da audit [DIRECTORY]`
Queries OSV vulnerability database for known CVEs.
- `--offline`: Use cached vulnerability data.

```bash
da audit .
da audit . --offline
```

#### `da licenses [DIRECTORY]`
Audits licenses against policy.

```bash
da licenses . --policy permissive
```

---

## 📊 Reporting Formats

- **`terminal` (Default):** Rich-formatted interactive tables with color severity tags.
- **`json`:** Full Pydantic report model serialization.
- **`markdown`:** Clean tables formatted for PR comments and technical docs.
- **`sarif`:** OASIS SARIF v2.1.0 standard for direct upload to **GitHub Code Scanning Alerts**.

---

## 📝 Configuration File Examples

### `envcheck.yml`
```yaml
version: "1.0"
variables:
  PORT:
    type: int
    required: true
    min: 1024
    max: 65535
  DATABASE_URL:
    type: url
    required: true
  APP_ENV:
    type: enum
    allowed: ["development", "staging", "production"]
    default: "development"
  DEBUG:
    type: bool
    required: false
```

### `ccx.yml`
```yaml
version: "1.0"
thresholds:
  max_cyclomatic: 10
  max_cognitive: 15
  max_loc: 50
  max_params: 5
  max_nesting_depth: 3
```

---

## 🤖 CI/CD Pipeline Integration (GitHub Actions)

Add `.github/workflows/code-toolkit.yml`:

```yaml
name: Code Quality & Security Audits

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  audit:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Source Code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Developer Code Toolkit
        run: |
          pip install -e shared/toolkit_common
          pip install -e packages/codebase-map
          pip install -e packages/env-checker
          pip install -e packages/dead-code-finder
          pip install -e packages/code-complexity-cli
          pip install -e packages/dependency-audit

      - name: 1. Validate Environment Configurations
        run: envcheck . --fail-on any

      - name: 2. Scan for Dead Code
        run: dcf scan . --min-confidence high

      - name: 3. Check Code Complexity Limits
        run: ccx report . --fail-on-threshold

      - name: 4. Audit Dependencies for CVEs & Licenses
        run: da scan . --fail-on-vuln

      - name: 5. Generate Codebase Architecture Diagram
        run: cbm diagram . -o docs/architecture.mmd
```

---

## 🧪 Testing

```bash
pytest -v
ruff check .
```

---

## 📄 License

Distributed under the [MIT License](LICENSE).

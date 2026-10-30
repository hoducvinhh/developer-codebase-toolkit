# Developer Code Quality & Analysis Toolkit (`developer-code-toolkit`)

An open-source collection of developer CLI tools for analyzing codebases, detecting code quality issues, auditing dependencies, measuring complexity, validating environment configurations, and detecting API breaking changes.

---

## 🛠️ Included Tools

| Tool | CLI Command | Package Path | Description |
| :--- | :--- | :--- | :--- |
| **Codebase Map** | `cbm` | [`packages/codebase-map`](packages/codebase-map) | Visualizes repo structure, entry points, architecture modules, and Mermaid graphs. |
| **Dead Code Finder** | `dcf` | [`packages/dead-code-finder`](packages/dead-code-finder) | Detects unused imports, variables, unreachable statements, and dead functions/classes. |
| **Dependency Audit** | `da` | [`packages/dependency-audit`](packages/dependency-audit) | Scans dependencies for CVEs (OSV database), outdated versions, duplicates, and license risks. |
| **Code Complexity CLI** | `ccx` | [`packages/code-complexity-cli`](packages/code-complexity-cli) | Measures Cyclomatic and Cognitive complexity, parameter counts, nesting, and ranks hotspots. |
| **Environment Checker** | `envcheck` | [`packages/env-checker`](packages/env-checker) | Compares `.env` against templates, validates types via schema, and redacts exposed credentials. |
| **API Diff** | `api-diff` | [`packages/api-diff`](packages/api-diff) | Compares OpenAPI 3.0/3.1 specs to detect and block breaking changes before release. |

---

## 🚀 Quick Start

### Installation

Each tool can be installed independently or all together:

```bash
# Install shared common library
pip install -e shared/toolkit_common

# Install individual CLI packages
pip install -e packages/codebase-map
pip install -e packages/env-checker
pip install -e packages/api-diff
pip install -e packages/dead-code-finder
pip install -e packages/code-complexity-cli
pip install -e packages/dependency-audit
```

### Common CLI Options

All tools support standardized options:
- `--format`: Choose output style (`terminal`, `json`, `markdown`, `sarif`).
- `--output` / `-o`: Save report to a file.
- `--quiet` / `-q`: Suppress informational messages.
- `--verbose` / `-v`: Print debug traces.
- `--no-color`: Disable ANSI color formatting.

### Standard Exit Codes

| Code | Status | Meaning |
| :--- | :--- | :--- |
| **0** | `SUCCESS` | Clean run with no blocking findings. |
| **1** | `BLOCKING_FINDINGS` | Violations or breaking changes exceeded configured threshold. |
| **2** | `INVALID_CONFIG` | Bad arguments or malformed configuration file. |
| **3** | `RUNTIME_ERROR` | An unhandled exception or parsing failure occurred. |
| **4** | `UNSUPPORTED` | Input format or ecosystem is unsupported. |

---

## 📖 Usage Examples

### 1. Codebase Map (`cbm`)
```bash
# Analyze repository architecture and entry points
cbm analyze .

# Render directory hierarchy tree
cbm tree . --depth 2

# Generate architecture Mermaid flowchart
cbm diagram .
```

### 2. Environment Checker (`envcheck`)
```bash
# Compare .env against .env.example and scan for secret leaks
envcheck .

# Validate environment types against schema
envcheck validate .env --schema envcheck.yml
```

### 3. API Diff (`api-diff`)
```bash
# Compare old and new OpenAPI specifications
api-diff openapi-v1.json openapi-v2.json --fail-on breaking
```

### 4. Dead Code Finder (`dcf`)
```bash
# Scan repository for unused imports and dead code
dcf scan . --min-confidence high
```

### 5. Code Complexity CLI (`ccx`)
```bash
# Identify top complexity hotspots
ccx hotspots . --top 5

# Analyze single file maintainability metrics
ccx analyze src/main.py
```

### 6. Dependency Audit (`da`)
```bash
# Audit packages, licenses, and security advisories (OSV)
da scan . --offline
```

---

## 🧪 Testing

Run all unit and integration test suites:
```bash
pytest -v
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

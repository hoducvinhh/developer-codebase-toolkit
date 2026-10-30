# Developer Code Quality & Analysis Toolkit
An open-source collection of developer CLI tools for analyzing codebases, detecting code quality issues, auditing dependencies, measuring complexity, validating environment configurations, and detecting API breaking changes.

- **Project name:** Developer Code Quality & Analysis Toolkit
- **Repository name:** `developer-code-toolkit`
- **Project type:** Open Source CLI Toolkit
- **Specification version:** 1.0
- **Status:** Initial Development

---

## 1. Project Overview

### 1.1. Vision
Build a collection of practical, reliable, and extensible CLI tools that help software developers understand, analyze, and improve code quality.

The toolkit consists of six independent tools:
1. **codebase-map (`cbm`)**: Visualize codebase structure and dependencies.
2. **dead-code-finder (`dcf`)**: Detect potentially unused code.
3. **dependency-audit (`da`)**: Analyze dependencies and security risks.
4. **code-complexity-cli (`ccx`)**: Measure code complexity and maintainability.
5. **env-checker (`envcheck`)**: Validate environment variables and configuration consistency.
6. **api-diff (`api-diff`)**: Compare API specifications and detect breaking changes.

Each tool must work independently without requiring the other tools.

The toolkit should prioritize:
- Developer productivity.
- Accurate analysis.
- Actionable reports.
- Safe execution.
- Low setup complexity.
- Extensibility.
- Cross-platform compatibility.
- Open Source community adoption.

### 1.2. Problem Statement
Software developers frequently encounter code quality and maintenance problems:
- Large codebases are difficult to understand.
- Unused code accumulates over time.
- Dependencies become outdated or vulnerable.
- Complex functions become difficult to maintain.
- Environment configurations become inconsistent.
- API changes introduce unexpected breaking changes.
- Existing tools often focus on one narrow problem.
- Developers need multiple tools with inconsistent interfaces and output formats.

This toolkit aims to provide a unified developer experience through six focused CLI utilities.

### 1.3. Product Goals
The toolkit must:
- Provide six independently usable CLI tools.
- Support common programming languages and development ecosystems.
- Generate useful reports.
- Support human-readable and machine-readable output.
- Provide actionable recommendations.
- Detect issues without modifying source code by default.
- Support CI/CD integration.
- Support configurable analysis rules.
- Provide deterministic results where possible.
- Remain extensible for future tools.

### 1.4. Non-goals
The toolkit will NOT:
- Replace IDEs.
- Replace language compilers.
- Replace all existing static analysis tools.
- Automatically refactor application source code.
- Automatically update dependencies.
- Automatically modify production configurations.
- Guarantee detection of every dead-code or security issue.
- Require an external AI service.
- Require developers to install all six tools.

---

## 2. Target Users

**Primary users:**
- Backend Developers
- Frontend Developers
- Full-stack Developers
- DevOps Engineers
- Software Architects
- Tech Leads
- Open Source Maintainers
- Engineering Teams
- CI/CD Engineers

**Typical scenarios:**
- Understanding an unfamiliar repository.
- Finding unused code before refactoring.
- Auditing project dependencies.
- Identifying complex functions.
- Checking environment configuration before deployment.
- Detecting API breaking changes before release.
- Integrating quality checks into CI pipelines.

---

## 3. Product Architecture

### 3.1. Monorepo Strategy
Use a monorepo containing six independent CLI packages.

Each CLI must:
- Have its own command.
- Have independent dependencies where practical.
- Have its own documentation.
- Have independent tests.
- Be independently installable.
- Support standalone execution.
- Avoid requiring other CLI packages.

Shared utilities may be provided through a lightweight internal library (`toolkit_common`).

### 3.2. CLI Commands
| Tool | Command | Main responsibility |
| :--- | :--- | :--- |
| codebase-map | `cbm` | Codebase structure and dependency visualization |
| dead-code-finder | `dcf` | Unused code detection |
| dependency-audit | `da` | Dependency and security analysis |
| code-complexity-cli | `ccx` | Code complexity measurement |
| env-checker | `envcheck` | Environment configuration validation |
| api-diff | `api-diff` | API specification comparison |

### 3.3. Shared CLI Experience
All six tools should follow consistent conventions.

**Common options:**
- `--help`
- `--version`
- `--config`
- `--format` (`terminal`, `json`, `markdown`, `sarif`)
- `--output`
- `--quiet`
- `--verbose`
- `--no-color`

**Exit Codes:**
| Code | Meaning |
| :--- | :--- |
| 0 | Successful execution, no configured blocking findings |
| 1 | Analysis completed but configured blocking findings exist |
| 2 | Invalid arguments or configuration |
| 3 | Analysis or runtime error |
| 4 | Unsupported project or input format |

**General Safety:**
- Read-only analysis by default.
- Never modify application source code automatically.
- Never print secret values.
- Handle symbolic links safely.
- Respect `.gitignore` where applicable.
- Exclude generated directories by default.
- Support configurable exclusions.
- Never execute arbitrary code from scanned repositories unless explicitly required and approved.

---

## 4. Project 1: Codebase Map (`cbm`)
- **Main purpose:** Helps developers understand unfamiliar or large codebases.
- **Core Requirements:**
  - `CBM-FR-01`: Repository discovery (root, languages, frameworks, manifests, entry points).
  - `CBM-FR-02`: Directory structure analysis (tree hierarchy, counts, language grouping, depth limit).
  - `CBM-FR-03`: Logical module detection (structure, package boundaries, framework conventions).
  - `CBM-FR-04`: Directed dependency graph analysis (files, modules, packages, internal vs external).
  - `CBM-FR-05`: Entry point detection with supporting evidence (main, startup, CLI, worker).
  - `CBM-FR-06`: Architecture visualization via Mermaid diagrams.
  - `CBM-FR-07`: Multi-format export (Terminal, JSON, Markdown, Mermaid).
  - `CBM-FR-08`: Incremental / targeted directory analysis.
- **Initial Language Support:** TypeScript, JavaScript, Python (MVP).

---

## 5. Project 2: Dead Code Finder (`dcf`)
- **Main purpose:** Analyze source code and detect potentially unused code to reduce bloat safely.
- **Core Requirements:**
  - `DCF-FR-01`: Project language detection (TypeScript, JavaScript, Python MVP).
  - `DCF-FR-02`: Unused import detection.
  - `DCF-FR-03`: Unused variable detection (distinguish never read, assigned unread, ignored `_` prefix).
  - `DCF-FR-04`: Unused function / method detection.
  - `DCF-FR-05`: Unused class detection.
  - `DCF-FR-06`: Unused export detection (with external consumer uncertainty warnings).
  - `DCF-FR-07`: Unreachable code detection (after return, impossible branches).
  - `DCF-FR-08`: Dynamic usage awareness (reflection, dynamic imports, decorators, plugin hooks).
  - `DCF-FR-09`: Severity and confidence classification (High, Medium, Low).
  - `DCF-FR-10`: Safe analysis (strictly read-only, no automatic code deletion).

---

## 6. Project 3: Dependency Audit (`da`)
- **Main purpose:** Analyze dependencies for outdated packages, known CVEs, license risks, and health.
- **Core Requirements:**
  - `DA-FR-01`: Dependency discovery (npm, pnpm, yarn, pip, poetry, uv).
  - `DA-FR-02`: Dependency inventory extraction (direct/transitive, prod/dev, versions).
  - `DA-FR-03`: Outdated dependency detection with version distance reporting.
  - `DA-FR-04`: Vulnerability scanning using trusted sources (OSV API, GHSA).
  - `DA-FR-05`: Dependency health & maintenance metrics (abandoned, deprecated).
  - `DA-FR-06`: Duplicate dependency detection in tree.
  - `DA-FR-07`: License compliance analysis & policy checking.
  - `DA-FR-08`: Potentially unused direct dependency analysis.
  - `DA-FR-09`: Clear, actionable security recommendations.
  - `DA-FR-10`: Offline inventory and online vulnerability lookup modes.

---

## 7. Project 4: Code Complexity CLI (`ccx`)
- **Main purpose:** Measure complexity and maintainability of functions, classes, and modules.
- **Core Requirements:**
  - `CCX-FR-01`: Language detection (Python, JavaScript, TypeScript MVP).
  - `CCX-FR-02`: Cyclomatic complexity calculation.
  - `CCX-FR-03`: Cognitive complexity calculation (nesting penalties, complex flow).
  - `CCX-FR-04`: Function size metrics (lines of code, logical statements, parameter count, nesting depth).
  - `CCX-FR-05`: Class complexity (method count, size, public methods).
  - `CCX-FR-06`: File and module level aggregation.
  - `CCX-FR-07`: Configurable warning and failure thresholds (`ccx.yml`).
  - `CCX-FR-08`: Complexity hotspot ranking.
  - `CCX-FR-09`: Future historical comparison.
  - `CCX-FR-10`: Actionable refactoring recommendations based on metrics.

---

## 8. Project 5: Environment Checker (`envcheck`)
- **Main purpose:** Validate environment variables and configuration consistency before deployment.
- **Core Requirements:**
  - `ENV-FR-01`: Environment file discovery (`.env`, `.env.example`, `.env.test`, etc.).
  - `ENV-FR-02`: Safe variable extraction (quoted, multiline, export prefix; never print values).
  - `ENV-FR-03`: Missing variable detection across template vs target files.
  - `ENV-FR-04`: Environment consistency matrix (dev, staging, prod templates).
  - `ENV-FR-05`: Source code environment usage detection (`process.env`, `os.environ`, `os.getenv`).
  - `ENV-FR-06`: Type and format validation (string, integer, float, boolean, url, email, port, enum, range).
  - `ENV-FR-07`: Secret detection and automatic masking (`[REDACTED]`).
  - `ENV-FR-08`: Dedicated configuration schema (`envcheck.yml`).
  - `ENV-FR-09`: Non-interactive CI/CD validation with blocking exit codes.
  - `ENV-FR-10`: Safe fix suggestions for missing templates without auto-modifying `.env`.

---

## 9. Project 6: API Diff (`api-diff`)
- **Main purpose:** Compare OpenAPI specifications to detect breaking changes before release.
- **Core Requirements:**
  - `API-FR-01`: Input support for OpenAPI 3.0, OpenAPI 3.1 in JSON and YAML.
  - `API-FR-02`: Complete specification parsing and validation.
  - `API-FR-03`: Endpoint comparison (added, removed, changed method/params).
  - `API-FR-04`: Request schema comparison (fields added/removed/type changed, required modifications).
  - `API-FR-05`: Response schema comparison (fields removed/type changed, status codes).
  - `API-FR-06`: Authentication & security scheme comparison.
  - `API-FR-07`: Breaking change classification (Breaking, Potentially Breaking, Non-breaking, Informational).
  - `API-FR-08`: Detailed change explanations with old/new values.
  - `API-FR-09`: Clear compatibility summary report.
  - `API-FR-10`: Multi-format export (Terminal, JSON, Markdown).
  - `API-FR-11`: CI/CD integration with `--fail-on breaking`.
  - `API-FR-12`: Git revision comparison support.

---

## 10. Shared Technical Architecture & Conventions
- Primary language: Python (cross-platform, rich parsing, mature ecosystem).
- Shared internal library: `shared/toolkit_common`.
- CLI framework: Click / Typer with Rich formatting.
- Common report model: JSON Schema with `tool`, `version`, `project`, `summary`, and `findings`.
- Exit codes: 0 (clean), 1 (blocking findings), 2 (bad config/args), 3 (error), 4 (unsupported).
- Monorepo structure with standalone `pyproject.toml` per package.

---

## 11. Development Roadmap
- **Phase 0: Foundation:** Monorepo scaffolding, `toolkit_common`, common report model, CI pipelines.
- **Phase 1: First MVP:** `cbm` (Codebase Map), `envcheck` (Environment Checker), `api-diff` (API Diff).
- **Phase 2: Static Code Analysis:** `dcf` (Dead Code Finder), `ccx` (Code Complexity CLI).
- **Phase 3: Dependency Intelligence:** `da` (Dependency Audit).
- **Phase 4: Ecosystem Quality & Hardening:** Cross-platform tests, performance, docs, release automation.

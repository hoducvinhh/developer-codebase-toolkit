# CLI Reference Manual

Comprehensive command-line interface documentation for all 6 tools in the toolkit.

---

## 1. `cbm` (Codebase Map)

Visualizes codebase structure, architecture modules, entry points, and dependencies.

### Commands

#### `cbm analyze [DIRECTORY]`
Run comprehensive codebase architecture and structure analysis.
- Options:
  - `-f, --format [terminal|json|markdown|sarif]`
  - `-o, --output PATH`
  - `-q, --quiet`
  - `-v, --verbose`
  - `--no-color`

#### `cbm tree [DIRECTORY]`
Display file tree hierarchy and file counts.
- Options:
  - `-d, --depth INTEGER`: Maximum nesting depth (default: 3).

#### `cbm deps [DIRECTORY]`
Extract and summarize internal module imports and third-party packages.

#### `cbm diagram [DIRECTORY]`
Generate a Mermaid architecture flowchart.
- Options:
  - `--direction [TD|LR]`: Flowchart layout direction.

---

## 2. `envcheck` (Environment Checker)

Validates environment variables, `.env.example` templates, types, and exposed secrets.

### Commands

#### `envcheck [DIRECTORY]`
Full environment audit: compares `.env` with `.env.example`, validates schema, and searches for exposed credentials.

#### `envcheck compare <TEMPLATE> <TARGET>`
Compare a template file (e.g. `.env.example`) against a target file (e.g. `.env`).

#### `envcheck validate <ENV_FILE> --schema <SCHEMA_FILE>`
Validate variables against constraints in an `envcheck.yml` schema file.

#### `envcheck analyze-usage [DIRECTORY]`
Scan source code (`process.env`, `os.environ`, `os.getenv`) and cross-check against `.env.example`.

#### `envcheck secrets [DIRECTORY]`
Scan repository environment files for unredacted plaintext secret tokens.

---

## 3. `api-diff` (API Diff)

Compares OpenAPI specifications and flags breaking changes.

### Command
`api-diff <OLD_SPEC> <NEW_SPEC> [OPTIONS]`
- Options:
  - `--fail-on [breaking|potentially_breaking|none]`: Level that triggers exit code 1.
  - `-f, --format [terminal|json|markdown|sarif]`
  - `-o, --output PATH`

---

## 4. `dcf` (Dead Code Finder)

Identifies unused imports, variables, unreachable statements, and dead functions.

### Command
`dcf scan [DIRECTORY] [OPTIONS]`
- Options:
  - `--min-confidence [low|medium|high]`
  - `--include-exports`: Flag potentially unused public export symbols.
  - `--fail-on-findings`: Exit with code 1 if findings exist.

---

## 5. `ccx` (Code Complexity CLI)

Measures Cyclomatic and Cognitive complexity, parameter counts, and function size.

### Commands

#### `ccx report [DIRECTORY]`
Comprehensive complexity report checking against thresholds.

#### `ccx hotspots [DIRECTORY]`
Rank top complexity hotspots.
- Options:
  - `-n, --top INTEGER`: Number of top hotspots to list (default: 10).

#### `ccx analyze <FILE_PATH>`
Inspect function-by-function complexity metrics for a single file.

---

## 6. `da` (Dependency Audit)

Audits dependencies for vulnerabilities, outdated versions, duplicates, and license risks.

### Commands

#### `da scan [DIRECTORY]`
Complete dependency audit including duplicate package detection, license compliance, and OSV vulnerabilities.

#### `da audit [DIRECTORY]`
Query OSV vulnerability database.
- Options:
  - `--offline`: Use cached vulnerability data only.

#### `da licenses [DIRECTORY]`
Check dependency licenses against compliance policy.
- Options:
  - `--policy [permissive|copyleft]`

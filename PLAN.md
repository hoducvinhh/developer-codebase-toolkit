# Master Implementation Plan: Developer Code Quality & Analysis Toolkit (`developer-code-toolkit`)

> **Mục tiêu:** Xây dựng monorepo mã nguồn mở gồm 6 công cụ dòng lệnh (CLI) độc lập, phục vụ phân tích chất lượng mã nguồn, phát hiện dead code, audit phụ thuộc, đo lường độ phức tạp, kiểm tra cấu hình môi trường và phát hiện breaking change của API.

---

## 1. Tổng quan Kiến trúc & Nguyên tắc cốt lõi

### 1.1. Nguyên tắc thiết kế (Core Tenets)
1. **Độc lập tuyệt đối (Zero Coupled Lifecycles):** Mỗi CLI package trong thư mục `packages/` có `pyproject.toml` riêng, có thể cài đặt riêng lẻ (`pip install -e packages/codebase-map`) mà không yêu cầu 5 công cụ còn lại.
2. **Thư viện nền tảng gọn nhẹ (`toolkit_common`):** Cung cấp các abstractions không thể thiếu:
   - Hệ thống mã thoát chuẩn (Exit Codes 0, 1, 2, 3, 4).
   - Bộ cờ CLI chuẩn hóa (`--format`, `--output`, `--quiet`, `--verbose`, `--no-color`, `--config`).
   - Mô hình báo cáo thống nhất (Pydantic schema) hỗ trợ Terminal (Rich), JSON, Markdown, SARIF v2.1.0.
   - Trình duyệt file an toàn (`SafeWalker`) tôn trọng `.gitignore`, kiểm soát symlink và giới hạn độ sâu.
   - Bộ phát hiện và ẩn thông tin nhạy cảm (`SecretRedactor`) để không bao giờ in secret ra màn hình.
3. **An toàn khi chạy (Read-only by default):** Không tự động ghi đè/sửa code nguồn hay lockfile trừ khi có cờ đặc biệt được cấp quyền tường minh.
4. **Phân cấp thực hiện theo Phase:** Tuân thủ lộ trình phân kỳ của `PROJECT_SPEC.md` để đảm bảo code đến đâu kiểm thử hoàn chỉnh đến đó.

---

## 2. Bản đồ Cấu trúc Thư mục Monorepo

```text
developer-code-toolkit/
├── PROJECT_SPEC.md                 # Toàn bộ đặc tả kỹ thuật dự án
├── PLAN.md                         # Kế hoạch triển khai kỹ thuật chi tiết
├── README.md                       # Tài liệu tổng quan dự án
├── LICENSE                         # Giấy phép mã nguồn mở (MIT / Apache-2.0)
├── CONTRIBUTING.md                  # Hướng dẫn đóng góp
├── pyproject.toml                  # Cấu hình workspace dev, ruff, pytest
│
├── shared/
│   └── toolkit_common/             # Thư viện dùng chung
│       ├── pyproject.toml
│       ├── README.md
│       ├── src/toolkit_common/
│       │   ├── __init__.py
│       │   ├── cli/
│       │   │   ├── base.py         # Click base decorator, options chung
│       │   │   └── exit_codes.py   # Enum mã thoát (0..4)
│       │   ├── config/
│       │   │   └── loader.py       # YAML/TOML/JSON config parser
│       │   ├── filesystem/
│       │   │   ├── walker.py       # SafeWalker, sandbox containment
│       │   │   └── gitignore.py    # Gitignore pattern matching
│       │   ├── logging/
│       │   │   └── logger.py       # Structured logger
│       │   ├── reporting/
│       │   │   ├── models.py       # Pydantic: Report, Finding, Summary
│       │   │   └── formatters/     # terminal.py, json.py, markdown.py, sarif.py
│       │   └── secrets/
│       │       ├── patterns.py     # Regex nhận diện API key, token, credentials
│       │       └── redactor.py     # Hàm mask [REDACTED]
│       └── tests/
│
├── packages/
│   ├── codebase-map/               # Tool 1: cbm
│   │   ├── pyproject.toml
│   │   ├── src/codebase_map/
│   │   │   ├── cli.py              # CLI entry point: cbm analyze, tree, deps, diagram
│   │   │   ├── discovery.py        # Phát hiện ngôn ngữ, frameworks, manifests
│   │   │   ├── tree.py             # Sinh cây thư mục và thống kê
│   │   │   ├── modules.py          # Phát hiện module logic
│   │   │   ├── dependencies.py     # Quét import, dựng đồ thị phụ thuộc
│   │   │   ├── entrypoints.py      # Heuristic nhận diện file chạy chính
│   │   │   └── mermaid.py          # Render sơ đồ Mermaid
│   │   └── tests/
│   │
│   ├── env-checker/                # Tool 5: envcheck
│   │   ├── pyproject.toml
│   │   ├── src/env_checker/
│   │   │   ├── cli.py              # CLI entry point: envcheck, compare, validate, secrets
│   │   │   ├── parser.py           # Parse .env (quotes, multiline, comments)
│   │   │   ├── schema.py           # Validate types (int, url, enum, port, range)
│   │   │   ├── comparator.py       # So khớp template (.env.example) và actual
│   │   │   ├── usage_scanner.py    # Quét AST/regex process.env, os.environ
│   │   │   └── secrets.py          # Quét secret bị commit
│   │   └── tests/
│   │
│   ├── api-diff/                   # Tool 6: api-diff
│   │   ├── pyproject.toml
│   │   ├── src/api_diff/
│   │   │   ├── cli.py              # CLI entry point: api-diff old new
│   │   │   ├── parser.py           # Parse OpenAPI 3.0 / 3.1 (JSON/YAML) + $ref resolver
│   │   │   ├── endpoint_diff.py    # So sánh endpoints, HTTP methods, paths
│   │   │   ├── schema_diff.py      # So sánh request/response schema, enums, required
│   │   │   ├── auth_diff.py        # So sánh cơ chế xác thực security schemes
│   │   │   └── classifier.py       # Phân loại Breaking / Non-breaking
│   │   └── tests/
│   │
│   ├── dead-code-finder/           # Tool 2: dcf (Phase 2)
│   │   ├── pyproject.toml
│   │   ├── src/dead_code_finder/
│   │   │   ├── cli.py              # CLI: dcf scan
│   │   │   ├── ast_python.py       # Phân tích AST Python
│   │   │   ├── ast_javascript.py   # Phân tích AST / tokenizer JS/TS
│   │   │   ├── symbol_table.py     # Bảng ký hiệu và liên kết tham chiếu
│   │   │   └── analyzer.py         # Phát hiện unused imports/vars/funcs/classes/exports
│   │   └── tests/
│   │
│   ├── code-complexity-cli/        # Tool 4: ccx (Phase 2)
│   │   ├── pyproject.toml
│   │   ├── src/code_complexity/
│   │   │   ├── cli.py              # CLI: ccx report, hotspots, analyze
│   │   │   ├── cyclomatic.py       # Đo Cyclomatic Complexity
│   │   │   ├── cognitive.py        # Đo Cognitive Complexity (nesting penalty)
│   │   │   ├── metrics.py          # Đo LOC, LLOC, parameter count, nesting depth
│   │   │   └── ranker.py           # Xếp hạng hotspots và cảnh báo theo threshold
│   │   └── tests/
│   │
│   └── dependency-audit/           # Tool 3: da (Phase 3)
│       ├── pyproject.toml
│       ├── src/dependency_audit/
│       │   ├── cli.py              # CLI: da scan, audit, outdated, licenses
│       │   ├── manifests/          # Parser package.json, requirements.txt, poetry.lock, pnpm
│       │   ├── osv_client.py       # Client tra cứu OSV API với local cache
│       │   ├── outdated.py         # Kiểm tra khoảng cách phiên bản (semver distance)
│       │   ├── licenses.py         # Kiểm tra giấy phép hợp lệ/vi phạm chính sách
│       │   └── health.py           # Đánh giá rủi ro bảo trì
│       └── tests/
│
├── docs/                           # Tài liệu chi tiết
├── examples/                       # Dự án mẫu làm test fixtures
└── .github/workflows/              # CI/CD tự động
```

---

## 3. Kế hoạch Hành động Chi tiết theo Từng Phase

### Phase 0: Nền tảng Dùng chung (`toolkit_common`) & Workspace Setup
- [x] **Bước 0.1: Khởi tạo Root Workspace**
  - Tạo `pyproject.toml` ở thư mục gốc cấu hình workspace, pytest và ruff.
  - Thiết lập `.gitignore` chuẩn cho Python, Node.js và các artifacts phân tích.
- [x] **Bước 0.2: Xây dựng Module `toolkit_common.cli`**
  - Định nghĩa chuẩn `ExitCode` enum:
    - `0`: SUCCESS (Thành công, không có blocking finding).
    - `1`: BLOCKING_FINDINGS (Có lỗi vi phạm chính sách / breaking change).
    - `2`: INVALID_CONFIG (Sai tham số dòng lệnh hoặc lỗi cú pháp config).
    - `3`: RUNTIME_ERROR (Lỗi phân tích hoặc runtime).
    - `4`: UNSUPPORTED (Dự án hoặc định dạng file không được hỗ trợ).
  - Tạo decorator hoặc Click group chuẩn hóa các cờ: `--format [terminal|json|markdown|sarif]`, `--output`, `--config`, `--quiet`, `--verbose`, `--no-color`.
- [x] **Bước 0.3: Xây dựng Module `toolkit_common.reporting`**
  - Định nghĩa Pydantic Models:
    - `Finding`: rule_id, severity (low, medium, high, critical), confidence (low, medium, high), file, line, column, symbol, message, suggestion.
    - `Report`: tool, version, project, timestamp, summary, findings, blocking_count.
  - Cài đặt các Formatters:
    - `TerminalFormatter`: Dùng Rich hoặc ANSI fallback hiển thị bảng kết quả rõ ràng, màu sắc theo severity.
    - `JsonFormatter`: Xuất JSON chuẩn hóa.
    - `MarkdownFormatter`: Xuất Markdown phục vụ GitHub PR summary.
    - `SarifFormatter`: Xuất chuẩn SARIF v2.1.0 cho GitHub Security Scanning.
- [x] **Bước 0.4: Xây dựng Module `toolkit_common.filesystem` (`SafeWalker`)**
  - Giới hạn quét trong phạm vi thư mục chỉ định, chặn symlink trỏ ra ngoài repo.
  - Phân tích và áp dụng các quy tắc bỏ qua từ `.gitignore`.
  - Mặc định loại trừ: `node_modules`, `venv`, `.git`, `dist`, `build`, `__pycache__`, `.pytest_cache`.
- [x] **Bước 0.5: Xây dựng Module `toolkit_common.secrets` (`SecretRedactor`)**
  - Nhận diện API key, Private Key, Bearer Token, Database URL có chứa password bằng regex + Shannon entropy.
  - Tự động thay thế giá trị nhạy cảm thành `[REDACTED]`.
- [x] **Bước 0.6: Viết Unit Test cho `toolkit_common`**
  - Kiểm thử đầy đủ các module: exit codes, models, formatters, walker, secret redactor.

---

### Phase 1: Bộ 3 Công cụ MVP (`cbm`, `envcheck`, `api-diff`)

#### 1. Công cụ 1: `codebase-map` (`cbm`)
- [x] **Bước 1.1: Trình khám phá Repository (`discovery.py`)**
  - Nhận diện các ngôn ngữ chủ đạo (Python, TypeScript, JavaScript).
  - Định danh frameworks (FastAPI, Flask, Express, Next.js, Django) và package managers.
- [x] **Bước 1.2: Trình phân tích cây thư mục (`tree.py`)**
  - Sinh cây cấu trúc hiển thị số lượng file, nhóm file theo ngôn ngữ, hỗ trợ `--depth`.
- [x] **Bước 1.3: Trình phân tích Module & Entry points (`modules.py`, `entrypoints.py`)**
  - Định vị các entry point (`main.py`, `index.ts`, `app.py`, `server.ts`) kèm bằng chứng nhận diện.
- [x] **Bước 1.4: Phân tích đồ thị phụ thuộc (`dependencies.py`)**
  - Quét `import`/`from` trong Python, `import`/`require` trong JS/TS.
  - Tách bạch rõ ràng Internal Dependencies và External Packages.
- [x] **Bước 1.5: Xuất sơ đồ Mermaid (`mermaid.py`)**
  - Xuất code Mermaid hợp lệ (`flowchart TD`, `graph LR`).
- [x] **Bước 1.6: Hoàn thiện CLI `cbm` & Viết Test Suite**
  - Cài đặt các lệnh: `cbm analyze`, `cbm tree`, `cbm deps`, `cbm diagram`.
  - Tạo fixture test repo mẫu và kiểm thử tự động.

#### 2. Công cụ 2: `env-checker` (`envcheck`)
- [x] **Bước 1.7: Bộ phân tích `.env` an toàn (`parser.py`)**
  - Hỗ trợ comment, giá trị trong ngoặc kép/đơn, biến rỗng, biến multiline, tiền tố `export`.
  - Không bao giờ lưu hay log giá trị thật ở dạng plaintext nếu nghi ngờ là secret.
- [x] **Bước 1.8: Trình so sánh cấu hình (`comparator.py`)**
  - So sánh file thực tế (`.env`) với file mẫu (`.env.example`), phát hiện biến thiếu, biến thừa.
- [x] **Bước 1.9: Kiểm tra định dạng theo Schema (`schema.py`)**
  - Hỗ trợ cấu hình `envcheck.yml` với các kiểu dữ liệu: `integer`, `boolean`, `url`, `email`, `port`, `enum`, `range`.
- [x] **Bước 1.10: Quét tham chiếu biến môi trường trong code (`usage_scanner.py`)**
  - Dùng AST (Python) và Scanner (JS/TS) phát hiện `process.env.VAR` và `os.environ['VAR']` / `os.getenv('VAR')`.
  - Đối chiếu với `.env.example` để cảnh báo biến dùng trong code nhưng chưa khai báo trong template.
- [x] **Bước 1.11: Hoàn thiện CLI `envcheck` & Viết Test Suite**
  - Cài đặt các lệnh: `envcheck`, `envcheck compare`, `envcheck validate`, `envcheck analyze-usage`, `envcheck secrets`.
  - Kiểm thử tự động với các kịch bản test case thực tế.

#### 3. Công cụ 3: `api-diff` (`api-diff`)
- [x] **Bước 1.12: Trình đọc OpenAPI 3.0 / 3.1 (`parser.py`)**
  - Hỗ trợ cả JSON và YAML. Tự động giải quyết các tham chiếu nội bộ `$ref`.
- [x] **Bước 1.13: Bộ so sánh Endpoints & Parameters (`endpoint_diff.py`)**
  - Phát hiện endpoint bị xóa, thêm mới, đổi method, đổi path parameters.
- [x] **Bước 1.14: Bộ so sánh Schema & Response (`schema_diff.py`)**
  - So sánh request body: thêm trường bắt buộc (breaking), xóa trường, đổi kiểu dữ liệu.
  - So sánh response: xóa trường (breaking), đổi cấu trúc status code.
- [x] **Bước 1.15: Phân loại Breaking Change (`classifier.py`)**
  - Phân loại 4 cấp độ: `Breaking`, `Potentially Breaking`, `Non-breaking`, `Informational`.
  - Trả về mã thoát `1` khi phát hiện breaking change và cờ `--fail-on breaking` được bật.
- [x] **Bước 1.16: Hoàn thiện CLI `api-diff` & Viết Test Suite**
  - Kiểm thử với các cặp OpenAPI spec mẫu (thay đổi an toàn vs phá vỡ tương thích).

---

### Phase 2: Bộ Công cụ Phân tích Tĩnh Code (`dcf`, `ccx`)

#### 1. Công cụ: `dead-code-finder` (`dcf`)
- [x] **Bước 2.1: Phân tích AST Python & Tokenizer JS/TS**
  - Thu thập bảng khai báo ký hiệu: hàm, biến, class, import, export.
- [x] **Bước 2.2: Trình đối chiếu Tham chiếu (Cross-file Reference Tracker)**
  - Xác định các import không bao giờ được dùng.
  - Xác định biến khai báo nhưng không đọc (bỏ qua biến bắt đầu bằng `_`).
  - Xác định hàm, class nội bộ không có ai gọi tới.
  - Xác định export không có file nào trong dự án import (cảnh báo nguy cơ false-positive với thư viện public).
- [x] **Bước 2.3: Hệ thống xếp hạng Độ tin cậy (Confidence Scorer)**
  - Gán nhãn `High` (import cục bộ không dùng), `Medium` (hàm helper nội bộ), `Low` (các hàm có thể được gọi động qua decorator / reflection).
- [x] **Bước 2.4: Hoàn thiện CLI `dcf` & Test Suite**
  - Lệnh: `dcf scan [DIR] [--min-confidence] [--include-exports]`.

#### 2. Công cụ: `code-complexity-cli` (`ccx`)
- [x] **Bước 2.5: Bộ đo Cyclomatic Complexity**
  - Tính điểm rẽ nhánh: `if`, `elif`, `for`, `while`, `except`, `match/case`, toán tử logic `and`/`or`.
- [x] **Bước 2.6: Bộ đo Cognitive Complexity**
  - Tính điểm nhận thức dựa trên mức độ lồng nhau (nesting depth penalty) và luồng xử lý phi tuyến tính.
- [x] **Bước 2.7: Đo kích thước hàm & lớp**
  - Đo dòng lệnh thực tế (LOC, LLOC), số lượng tham số đầu vào, độ sâu lồng tối đa.
- [x] **Bước 2.8: Xếp hạng Hotspots & Cảnh báo theo ngưỡng (`ccx.yml`)**
  - Báo cáo danh sách các hàm/module phức tạp nhất cần tái cấu trúc.
- [x] **Bước 2.9: Hoàn thiện CLI `ccx` & Test Suite**
  - Lệnh: `ccx report`, `ccx hotspots`, `ccx analyze <file>`.

---

### Phase 3: Công cụ Trí tuệ Phụ thuộc (`dependency-audit` - `da`)
- [x] **Bước 3.1: Bộ đọc Manifests đa hệ sinh thái**
  - Đọc `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock` (Node.js).
  - Đọc `requirements.txt`, `pyproject.toml`, `poetry.lock` (Python).
- [x] **Bước 3.2: Tích hợp OSV Database API (`osv_client.py`)**
  - Gửi batch request kiểm tra lỗ hổng bảo mật đã biết theo Package + Version.
  - Cơ chế cache cục bộ giúp chạy offline (`--offline`).
- [x] **Bước 3.3: Kiểm tra phiên bản Outdated & Giấy phép (Licenses)**
  - Tính toán khoảng cách phiên bản (major, minor, patch).
  - Đối chiếu giấy phép phụ thuộc với danh sách policy cho phép / cấm.
- [x] **Bước 3.4: Phát hiện phụ thuộc trùng lặp và phụ thuộc không dùng**
  - Quét lockfile tìm nhiều phiên bản của cùng 1 package trong cây phụ thuộc.
- [x] **Bước 3.5: Hoàn thiện CLI `da` & Test Suite**
  - Lệnh: `da scan`, `da audit`, `da outdated`, `da licenses`.

---

### Phase 4: Hoàn thiện Hệ sinh thái, CI/CD & Tài liệu
- [x] **Bước 4.1: Xây dựng GitHub Actions Workflows**
  - `.github/workflows/tests.yml`: Chạy tự động ma trận test trên Ubuntu, Windows, macOS.
  - `.github/workflows/lint.yml`: Chạy `ruff check` và `ruff format --check`.
- [x] **Bước 4.2: Soạn thảo Tài liệu Đầy đủ**
  - `README.md` chính: Hướng dẫn cài đặt, quick start, bảng so sánh và ví dụ cho cả 6 công cụ.
  - `README.md` cho từng package trong `packages/*/`.
  - Tài liệu chi tiết trong `docs/` (`cli-reference.md`, `architecture.md`, `installation.md`).
- [x] **Bước 4.3: Kiểm thử toàn diện Cross-platform**
  - Xác minh tất cả 6 công cụ chạy mượt mà trên môi trường Windows và Linux.

---

## 4. Kế hoạch Kiểm thử & Tiêu chí Nghiệm thu (Verification Matrix)

| Công cụ | Lệnh kiểm thử tự động | Tiêu chí nghiệm thu cốt lõi |
| :--- | :--- | :--- |
| `toolkit_common` | `pytest shared/toolkit_common/tests` | Đảm bảo tính toán đúng exit code, format chuẩn Terminal/JSON/Markdown/SARIF, SafeWalker chặn traversal, ẩn secret 100%. |
| `codebase-map` | `pytest packages/codebase-map/tests` | Cây thư mục chính xác, nhận diện đúng entry point, sơ đồ Mermaid cú pháp chuẩn. |
| `env-checker` | `pytest packages/env-checker/tests` | Đọc đúng .env phức tạp, báo biến thiếu, bắt lỗi kiểu dữ liệu theo schema, quét đúng biến trong code nguồn. |
| `api-diff` | `pytest packages/api-diff/tests` | Nhận diện đúng breaking change (xóa endpoint, sửa kiểu dữ liệu response), trả mã thoát 1 khi có lỗi vi phạm. |
| `dead-code-finder` | `pytest packages/dead-code-finder/tests` | Bắt đúng unused imports, biến thừa; phân loại đúng confidence level High/Medium/Low; không xóa file người dùng. |
| `code-complexity-cli` | `pytest packages/code-complexity-cli/tests` | Tính chính xác cyclomatic & cognitive complexity theo mẫu chuẩn; xếp hạng hotspot chính xác theo threshold. |
| `dependency-audit` | `pytest packages/dependency-audit/tests` | Parse chính xác lockfiles; tra cứu lỗ hổng chính xác với mock OSV data; chạy tốt ở chế độ offline. |
| **All Tools** | `pytest` | Toàn bộ test suite vượt qua (0 failures), ruff lint 100% sạch. |

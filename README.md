# Developer Code Quality & Analysis Toolkit (`developer-code-toolkit`)

<div align="center">

**Bộ công cụ dòng lệnh (CLI) mã nguồn mở phục vụ phân tích chất lượng mã nguồn, phát hiện dead code, audit phụ thuộc, đo lường độ phức tạp, kiểm tra cấu hình môi trường và phát hiện breaking changes của API.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Tests: Pytest](https://img.shields.io/badge/Tests-36%20Passed-brightgreen.svg)](#-chạy-kiểm-thử-testing)

[🇻🇳 Tiếng Việt](README.md) | [🇬🇧 English](README.en.md)

</div>

---

## 📑 Mục lục
1. [Giới thiệu tổng quan](#-giới-thiệu-tổng-quan)
2. [Cấu trúc Monorepo & Danh sách 6 công cụ](#-cấu-trúc-monorepo--danh-sách-6-công-cụ)
3. [Hướng dẫn cài đặt](#-hướng-dẫn-cài-đặt)
4. [Tùy chọn chung (Common Options) & Mã thoát chuẩn (Exit Codes)](#-tùy-chọn-chung--mã-thoát-chuẩn)
5. [Hướng dẫn sử dụng chi tiết từng công cụ](#-hướng-dẫn-sử-dụng-chi-tiết-từng-công-cụ)
   - [1. `cbm` — Codebase Map](#1-cbm--codebase-map)
   - [2. `envcheck` — Environment Checker](#2-envcheck--environment-checker)
   - [3. `api-diff` — API Diff](#3-api-diff--api-diff)
   - [4. `dcf` — Dead Code Finder](#4-dcf--dead-code-finder)
   - [5. `ccx` — Code Complexity CLI](#5-ccx--code-complexity-cli)
   - [6. `da` — Dependency Audit](#6-da--dependency-audit)
6. [Định dạng báo cáo (Reporting Formats)](#-định-dạng-báo-cáo-reporting-formats)
7. [File cấu hình mẫu (Configuration Files)](#-file-cấu-hình-mẫu)
8. [Tích hợp CI/CD Pipeline (GitHub Actions)](#-tích-hợp-cicd-pipeline-github-actions)
9. [Chạy kiểm thử (Testing)](#-chạy-kiểm-thử-testing)
10. [Giấy phép (License)](#-giấy-phép-license)

---

## 🌟 Giới thiệu tổng quan

Trong quá trình phát triển và bảo trì phần mềm, các lập trình viên thường xuyên đối mặt với:
- Dự án mã nguồn lớn, khó nắm bắt kiến trúc và các luồng thực thi chính.
- Code thừa, import rác, biến không sử dụng tích tụ theo thời gian gây nặng dự án.
- Cấu hình file `.env` bị lệch giữa các môi trường (Dev/Staging/Prod) hoặc vô tình để lộ bí mật/API Key.
- Thay đổi cấu trúc API (OpenAPI) làm đứt gãy ứng dụng client/frontend mà không biết trước.
- Hàm quá dài, độ lồng nhau sâu (cyclomatic & cognitive complexity cao) gây khó test và bảo trì.
- Thư viện phụ thuộc chứa lỗ hổng bảo mật đã công bố (CVE) hoặc vi phạm chính sách bản quyền phần mềm (GPL, copyleft).

**`developer-code-toolkit`** giải quyết các vấn đề trên thông qua **6 công cụ dòng lệnh (CLI)** chuyên biệt, hoạt động độc lập, tuân thủ nguyên tắc an toàn tuyệt đối (**Read-Only by default**) và sẵn sàng tích hợp vào quy trình CI/CD.

---

## 🛠️ Cấu trúc Monorepo & Danh sách 6 công cụ

Dự án được tổ chức theo kiến trúc **Zero-Coupled Monorepo**. Mỗi package trong thư mục `packages/` có vòng đời riêng, file `pyproject.toml` riêng và có thể cài đặt độc lập mà không cần các công cụ khác. Thư viện [`shared/toolkit_common`](shared/toolkit_common) đóng vai trò làm nền tảng chia sẻ format báo cáo, mã thoát chuẩn, duyệt file an toàn và che giấu secret.

| Công cụ | Lệnh CLI | Thư mục Package | Mô tả chức năng |
| :--- | :--- | :--- | :--- |
| **Codebase Map** | `cbm` | [`packages/codebase-map`](packages/codebase-map) | Khảo sát cấu trúc repository, nhận diện framework/ngôn ngữ, liệt kê entry point và vẽ sơ đồ kiến trúc Mermaid. |
| **Environment Checker** | `envcheck` | [`packages/env-checker`](packages/env-checker) | So khớp `.env` với `.env.example`, xác thực kiểu dữ liệu theo schema, quét code tìm biến chưa khai báo và bắt lỗi lộ secret. |
| **API Diff** | `api-diff` | [`packages/api-diff`](packages/api-diff) | So sánh hai bản đặc tả OpenAPI 3.0/3.1 (JSON/YAML), tự động phát hiện và phân loại các breaking changes. |
| **Dead Code Finder** | `dcf` | [`packages/dead-code-finder`](packages/dead-code-finder) | Phân tích AST Python & JS/TS để tìm import thừa, biến/hàm mồ côi và mã không thể chạm tới (unreachable code). |
| **Code Complexity CLI** | `ccx` | [`packages/code-complexity-cli`](packages/code-complexity-cli) | Đo độ phức tạp Cyclomatic & Cognitive, đếm số tham số, đo độ sâu lồng nhau và xếp hạng các điểm nóng (hotspots). |
| **Dependency Audit** | `da` | [`packages/dependency-audit`](packages/dependency-audit) | Quét file manifest/lockfile để tra cứu lỗ hổng CVE từ OSV, phát hiện trùng lặp version và rà soát chính sách bản quyền. |

---

## 🚀 Hướng dẫn cài đặt

### Yêu cầu tiên quyết
- **Python:** Phiên bản `>= 3.10` (Hỗ trợ 3.10, 3.11, 3.12, 3.13, 3.14).
- **Trình quản lý gói:** `pip`.

### 1. Cài đặt toàn bộ bộ công cụ (Khuyến nghị cho nhà phát triển)

Clone repository và cài đặt các package ở chế độ chỉnh sửa trực tiếp (`editable mode`):

```bash
# Clone repository
git clone https://github.com/hoducvinhh/developer-codebase-toolkit.git
cd developer-codebase-toolkit

# 1. Cài đặt thư viện dùng chung bắt buộc
pip install -e shared/toolkit_common

# 2. Cài đặt lần lượt cả 6 công cụ CLI
pip install -e packages/codebase-map
pip install -e packages/env-checker
pip install -e packages/api-diff
pip install -e packages/dead-code-finder
pip install -e packages/code-complexity-cli
pip install -e packages/dependency-audit
```

### 2. Cài đặt chỉ riêng công cụ bạn cần

Do kiến trúc tách rời hoàn toàn, bạn hoàn toàn có thể chỉ cài những công cụ phục vụ mục đích hiện tại:

```bash
# Cài đặt nền tảng chung
pip install -e shared/toolkit_common

# Chỉ cài cbm và ccx để phân tích mã nguồn
pip install -e packages/codebase-map
pip install -e packages/code-complexity-cli
```

### 3. Kiểm tra cài đặt thành công

Chạy lệnh kiểm tra phiên bản của từng công cụ:

```bash
cbm --version
envcheck --version
api-diff --help
dcf --version
ccx --version
da --version
```

---

## ⚙️ Tùy chọn chung & Mã thoát chuẩn

### 1. Các cờ tham số chung (Common Options)
Tất cả các công cụ trong bộ toolkit đều tuân thủ bộ tham số dòng lệnh tiêu chuẩn:

| Cờ tham số | Dạng ngắn | Mặc định | Ý nghĩa |
| :--- | :--- | :--- | :--- |
| `-f, --format` | `-f` | `terminal` | Định dạng báo cáo: `terminal`, `json`, `markdown`, `sarif`. |
| `-o, --output` | `-o` | *(in ra stdout)* | Ghi nội dung báo cáo trực tiếp ra đường dẫn file chỉ định. |
| `-c, --config` | `-c` | *(tự tìm file)* | Chỉ định đường dẫn file cấu hình tùy chỉnh (`.yml` / `.toml` / `.json`). |
| `-q, --quiet` | `-q` | `false` | Chế độ im lặng: ẩn các thông tin tiến trình, chỉ in kết quả chính. |
| `-v, --verbose` | `-v` | `false` | Chế độ gỡ lỗi: in toàn bộ vết ngăn xếp (stack trace) khi có ngoại lệ. |
| `--no-color` | | `false` | Tắt định dạng màu ANSI (thích hợp khi lưu log thô vào CI). |

### 2. Bảng mã thoát tiêu chuẩn (Exit Codes)
Phục vụ việc tích hợp vào các script tự động hóa và pipeline CI/CD:

| Mã thoát | Trạng thái | Ý nghĩa |
| :---: | :--- | :--- |
| **0** | `SUCCESS` | Quá trình chạy hoàn tất trơn tru, không có vi phạm nào chạm ngưỡng chặn. |
| **1** | `BLOCKING_FINDINGS` | Hoàn thành phân tích nhưng phát hiện vi phạm/lỗi bảo mật/breaking change nghiêm trọng vượt ngưỡng. |
| **2** | `INVALID_CONFIG` | Tham số dòng lệnh không hợp lệ hoặc file cấu hình YAML/JSON bị lỗi cú pháp. |
| **3** | `RUNTIME_ERROR` | Xảy ra lỗi runtime không mong muốn hoặc không thể parse được file nguồn. |
| **4** | `UNSUPPORTED` | Định dạng file hoặc hệ sinh thái ngôn ngữ đầu vào chưa được hỗ trợ. |

---

## 📖 Hướng dẫn sử dụng chi tiết từng công cụ

---

### 1. `cbm` — Codebase Map

Công cụ trực quan hóa kiến trúc, cấu trúc cây thư mục, xác định điểm chạy chính (entry points) và xuất sơ đồ quan hệ Mermaid.

#### `cbm analyze [DIRECTORY]`
Phân tích toàn diện dự án: phát hiện ngôn ngữ chính, danh sách framework, tổng số dòng code, số module logic và các điểm chạy chính (file `main.py`, `index.ts`, `app.py`, CLI commands, Dockerfile...).

```bash
# Phân tích thư mục hiện tại
cbm analyze .

# Phân tích một dự án khác và xuất báo cáo dạng JSON
cbm analyze /path/to/project -f json -o repo-analysis.json
```

#### `cbm tree [DIRECTORY]`
Hiển thị sơ đồ cây thư mục trực quan và tính toán số lượng file.
- `-d, --depth INTEGER`: Giới hạn độ sâu thư mục (mặc định: `3`).

```bash
# Xem cây thư mục với độ sâu tối đa 2 cấp
cbm tree . --depth 2

# Xuất cây thư mục sang định dạng JSON
cbm tree . --depth 3 -f json -o tree.json
```

#### `cbm deps [DIRECTORY]`
Trích xuất và tổng hợp danh sách các import nội bộ giữa các module và danh sách các thư viện bên thứ ba mà dự án đang dùng.

```bash
cbm deps .
```

#### `cbm diagram [DIRECTORY]`
Tự động sinh mã biểu đồ kiến trúc dạng **Mermaid flowchart**. Bạn có thể copy mã này dán thẳng vào file Markdown trên GitHub hoặc tài liệu kỹ thuật.
- `--direction [TD|LR]`: Hướng vẽ sơ đồ (`TD`: Top-Down - trên xuống dưới, `LR`: Left-Right - trái sang phải. Mặc định: `TD`).
- `-o, --output PATH`: Lưu mã sơ đồ ra file `.mmd` hoặc `.md`.

```bash
# Sinh sơ đồ theo chiều dọc và in ra màn hình
cbm diagram .

# Sinh sơ đồ theo chiều ngang và lưu vào file
cbm diagram . --direction LR -o docs/architecture.mmd
```

---

### 2. `envcheck` — Environment Checker

Công cụ kiểm tra tính toàn vẹn của cấu hình môi trường, bảo vệ an toàn thông tin bí mật và đồng bộ file `.env`.

#### `envcheck [DIRECTORY]` *(Lệnh mặc định)*
Chạy kiểm toán tổng hợp môi trường trong thư mục:
1. So sánh `.env` với file mẫu `.env.example`.
2. Kiểm tra kiểu dữ liệu theo file quy chuẩn `envcheck.yml`.
3. Quét kiểm tra secret/token chưa được mã hóa.

- `--fail-on [missing|secret|schema|any]`: Chỉ định điều kiện kích hoạt Exit Code 1 (Mặc định: `missing`).

```bash
# Chạy kiểm tra môi trường trong thư mục hiện tại
envcheck .

# Báo lỗi thất bại (exit code 1) nếu có bất kỳ biến nào thiếu hoặc lộ secret
envcheck . --fail-on any
```

#### `envcheck compare <TEMPLATE> <TARGET>`
So khớp trực tiếp một file cấu hình mẫu (Template) với một file môi trường thực tế (Target) để tìm các biến bị thiếu (`ENV-MISSING`) hoặc biến thừa không được tài liệu hóa (`ENV-EXTRA`).

```bash
envcheck compare .env.example .env
envcheck compare .env.production.template .env.production
```

#### `envcheck validate <ENV_FILE> --schema <SCHEMA_FILE>`
Xác thực từng biến môi trường trong file `.env` dựa theo các ràng buộc định dạng trong file schema YAML.
- `-s, --schema PATH`: Đường dẫn file schema quy định kiểu (bắt buộc).

```bash
envcheck validate .env --schema envcheck.yml
```

#### `envcheck analyze-usage [DIRECTORY]`
Quét toàn bộ mã nguồn dự án (tìm các đoạn truy cập như `os.environ[...]`, `os.getenv(...)`, `process.env....`) và đối chiếu với file `.env.example` để phát hiện biến nào trong code đang dùng mà quên chưa khai báo tài liệu.
- `-t, --template PATH`: Đường dẫn file template (mặc định tìm `.env.example`).

```bash
envcheck analyze-usage .
```

#### `envcheck secrets [DIRECTORY]`
Quét toàn bộ thư mục và các file cấu hình để nhận diện các Secret, Private Key, API Token trần chưa được che giấu (sử dụng thuật toán Shannon Entropy kết hợp mẫu Regex độ nhạy cao).

```bash
envcheck secrets .
```

---

### 3. `api-diff` — API Diff

Công cụ kiểm tra tương thích ngược giữa các phiên bản API theo chuẩn OpenAPI / Swagger (hỗ trợ cả JSON và YAML).

#### `api-diff <OLD_SPEC> <NEW_SPEC> [OPTIONS]`
So sánh bản đặc tả cũ và bản đặc tả mới, tự động phát hiện:
- **Breaking changes:** Xóa endpoint, đổi HTTP method, thêm tham số `required: true`, đổi kiểu dữ liệu request/response, xóa mã status code thành công...
- **Potentially breaking changes:** Thay đổi cơ chế xác thực auth, nới lỏng hoặc siết chặt enum...
- **Non-breaking changes:** Thêm endpoint mới, thêm optional query param, cập nhật description...

**Các tùy chọn:**
- `--fail-on [breaking|potentially_breaking|none]`: Mức độ thay đổi sẽ kích hoạt Exit Code 1 (Mặc định: `breaking`).
- `-f, --format [terminal|json|markdown|sarif]`: Định dạng xuất.
- `-o, --output PATH`: Đường dẫn lưu báo cáo.

```bash
# So sánh 2 phiên bản và in báo cáo ra terminal
api-diff openapi-v1.json openapi-v2.json

# Chặn release nếu có breaking change và xuất file báo cáo Markdown cho Pull Request
api-diff openapi-v1.yaml openapi-v2.yaml --fail-on breaking -f markdown -o pr-comment.md
```

---

### 4. `dcf` — Dead Code Finder

Công cụ rà soát mã nguồn chết, import dư thừa và các biến mồ côi bằng cách phân tích Cây cú pháp trừu tượng (AST).

#### `dcf scan [DIRECTORY] [OPTIONS]`
Quét toàn bộ thư mục dự án để tìm:
- Thư viện import nhưng không bao giờ gọi tới (`DCF-UNUSED-IMPORT`).
- Biến cục bộ/toàn cục được gán giá trị nhưng không được đọc (`DCF-UNUSED-VARIABLE`).
- Các hàm/class nội bộ không có lời gọi (`DCF-DEAD-FUNCTION`, `DCF-DEAD-CLASS`).
- Các câu lệnh đứng sau `return`, `raise`, `break` không thể chạm tới (`DCF-UNREACHABLE-CODE`).

**Các tùy chọn:**
- `--min-confidence [low|medium|high]`: Ngưỡng độ tin cậy tối thiểu để hiển thị (Mặc định: `low`).
- `--include-exports`: Cờ kiểm tra cả các hàm/class công khai (public exports) không thấy file nào gọi.
- `--fail-on-findings`: Thoát với Exit Code 1 nếu phát hiện dead code đạt độ tin cậy cao.

```bash
# Quét tìm dead code trong thư mục hiện tại
dcf scan .

# Chỉ hiển thị các cảnh báo có độ chắc chắn cao (high confidence)
dcf scan . --min-confidence high

# Quét chặt chẽ bao gồm cả public exports và trả mã lỗi chặn CI
dcf scan src/ --include-exports --fail-on-findings
```

---

### 5. `ccx` — Code Complexity CLI

Đo lường độ phức tạp thuật toán và khả năng bảo trì của mã nguồn dựa trên hai thang đo:
- **Cyclomatic Complexity (McCabe):** Đo số lượng nhánh logic độc lập (rẽ nhánh `if`, `while`, `for`, `except`...).
- **Cognitive Complexity (Sonar):** Đo mức độ khó hiểu đối với não bộ con người khi đọc code (tính điểm theo độ lồng sâu của khối lệnh).

#### `ccx report [DIRECTORY]`
Quét toàn bộ file nguồn trong dự án và đối chiếu với các ngưỡng cấu hình tối đa.
- `--fail-on-threshold`: Thoát với Exit Code 1 nếu có bất kỳ hàm nào vượt ngưỡng phức tạp cho phép.
- `-c, --config PATH`: File cấu hình ngưỡng tùy biến (mặc định tìm `ccx.yml`).

```bash
# Tạo báo cáo tổng quan độ phức tạp của dự án
ccx report .

# Kiểm tra và chặn build nếu vượt ngưỡng quy định
ccx report . --fail-on-threshold
```

#### `ccx hotspots [DIRECTORY]`
Liệt kê và xếp hạng các hàm phức tạp nhất ("điểm nóng") cần ưu tiên refactor trong dự án.
- `-n, --top INTEGER`: Số lượng điểm nóng muốn hiển thị (Mặc định: `10`).

```bash
# Tìm Top 5 hàm phức tạp nhất
ccx hotspots . --top 5

# Xuất danh sách Top 10 hotspots ra file JSON
ccx hotspots . -n 10 -f json -o hotspots.json
```

#### `ccx analyze <FILE_PATH>`
Phân tích chi tiết từng hàm trong một file mã nguồn cụ thể (dòng bắt đầu/kết thúc, số dòng LOC, độ sâu lồng tối đa, số lượng tham số đầu vào, điểm Cyclomatic và Cognitive).

```bash
ccx analyze packages/codebase-map/src/codebase_map/dependencies.py
```

---

### 6. `da` — Dependency Audit

Công cụ bảo vệ an toàn chuỗi cung ứng phần mềm (Software Supply Chain Security), hỗ trợ các file manifest như `requirements.txt`, `pyproject.toml`, `package.json`,...

#### `da scan [DIRECTORY]`
Quét kiểm toán phụ thuộc đa tầng:
1. **Trùng lặp phiên bản (`DA-DUPLICATE-DEPENDENCY`):** Phát hiện cùng một thư viện nhưng kéo về nhiều version khác nhau trong cây phụ thuộc.
2. **Vi phạm chính sách giấy phép (`DA-LICENSE-VIOLATION`):** Rà soát các gói sử dụng bản quyền cấm hoặc có tính lây lan (copyleft/GPL).
3. **Lỗ hổng bảo mật (`DA-VULN-*`):** Tra cứu trực tiếp với cơ sở dữ liệu lỗ hổng bảo mật nguồn mở **OSV** (Open Source Vulnerabilities).

- `--policy [permissive|copyleft]`: Chọn chính sách bản quyền áp dụng (Mặc định: `permissive` - chỉ cho phép giấy phép mở như MIT, Apache, BSD...).
- `--offline`: Chỉ sử dụng cache đã lưu (`.osv_cache.json`), không gọi API mạng ra ngoài.
- `--fail-on-vuln`: Thoát với Exit Code 1 nếu tồn tại bất kỳ lỗ hổng CVE nào.

```bash
# Quét phụ thuộc toàn diện
da scan .

# Quét kiểm tra giấy phép với chính sách cho phép cả copyleft
da scan . --policy copyleft

# Chặn CI nếu có lỗ hổng CVE
da scan . --fail-on-vuln
```

#### `da audit [DIRECTORY]`
Chỉ tập trung tra cứu và báo cáo danh sách các lỗ hổng bảo mật (CVE/GHSA) tìm thấy trong dependencies.
- `--offline`: Chế độ tra cứu offline từ file cache.

```bash
da audit .
da audit . --offline
```

#### `da licenses [DIRECTORY]`
Chỉ kiểm tra tính tuân thủ chính sách bản quyền phần mềm đối với tất cả dependencies.

```bash
da licenses . --policy permissive
```

---

## 📊 Định dạng báo cáo (Reporting Formats)

Mọi công cụ đều hỗ trợ xuất kết quả qua tham số `-f, --format`:

1. **`terminal` (Mặc định):**
   - Sử dụng thư viện `rich` để vẽ bảng màu sắc, biểu tượng trực quan, tóm tắt số lượng phát hiện theo mức độ nghiêm trọng (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
2. **`json`:**
   - Dữ liệu có cấu trúc đầy đủ chuẩn Pydantic schema, phù hợp để tích hợp với các tool khác hoặc lưu trữ cơ sở dữ liệu.
3. **`markdown`:**
   - Xuất bảng biểu và tóm tắt theo định dạng Markdown, rất lý tưởng để tự động tạo bình luận (comment) vào Pull Request trên GitHub/GitLab.
4. **`sarif` (Static Analysis Results Interchange Format):**
   - Chuẩn định dạng trao đổi phân tích tĩnh quốc tế (OASIS SARIF v2.1.0). Tương thích trực tiếp để upload lên tab **GitHub Code Scanning Alerts**.

---

## 📝 File cấu hình mẫu

### 1. File cấu hình schema môi trường: `envcheck.yml`
Đặt file này tại thư mục gốc dự án để `envcheck validate` tự động đọc:

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
  API_TIMEOUT_SECONDS:
    type: int
    min: 1
    max: 120
```

### 2. File cấu hình ngưỡng độ phức tạp: `ccx.yml`
Đặt tại thư mục gốc để `ccx report` tự động áp dụng ngưỡng giới hạn:

```yaml
version: "1.0"
thresholds:
  max_cyclomatic: 10       # Điểm Cyclomatic tối đa cho 1 hàm
  max_cognitive: 15        # Điểm Cognitive tối đa cho 1 hàm
  max_loc: 50              # Số dòng code tối đa của 1 hàm
  max_params: 5            # Số lượng tham số tối đa
  max_nesting_depth: 3     # Độ sâu lồng khối lệnh (if/for/while) tối đa
```

---

## 🤖 Tích hợp CI/CD Pipeline (GitHub Actions)

Tạo file `.github/workflows/code-toolkit.yml` để tự động hóa kiểm tra chất lượng mã nguồn mỗi khi có commit hoặc Pull Request:

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
        run: |
          envcheck . --fail-on any

      - name: 2. Scan for Dead Code
        run: |
          dcf scan . --min-confidence high

      - name: 3. Check Code Complexity Limits
        run: |
          ccx report . --fail-on-threshold

      - name: 4. Audit Dependencies for CVEs & Licenses
        run: |
          da scan . --fail-on-vuln

      - name: 5. Generate Codebase Architecture Diagram
        run: |
          cbm diagram . -o docs/architecture.mmd
```

---

## 🧪 Chạy kiểm thử (Testing)

Dự án đi kèm bộ kiểm thử toàn diện cho cả thư viện dùng chung và 6 gói công cụ CLI.

```bash
# Chạy toàn bộ 36 bài test unit & integration
pytest -v

# Chạy kiểm tra định dạng code với Ruff
ruff check .
```

---

## 📄 Giấy phép (License)

Dự án này được phân phối dưới giấy phép mã nguồn mở [MIT License](LICENSE). Bạn hoàn toàn tự do sử dụng, chỉnh sửa và đóng góp cho cộng đồng.

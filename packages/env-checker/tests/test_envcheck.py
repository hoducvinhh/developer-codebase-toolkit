from pathlib import Path

from click.testing import CliRunner
from env_checker.cli import main
from env_checker.comparator import compare_env_files
from env_checker.parser import parse_env_file
from env_checker.schema import SchemaRule, validate_variable
from env_checker.secrets import audit_env_secrets
from env_checker.usage_scanner import scan_codebase_usages


def test_env_parser(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        """
# Database configuration
export DB_PORT=5432
DB_HOST="localhost"
API_KEY='sec-12345'
EMPTY_VAL=
MULTILINE="first line
second line"
""",
        encoding="utf-8",
    )
    res = parse_env_file(env_file)
    assert res.variables["DB_PORT"].value == "5432"
    assert res.variables["DB_HOST"].value == "localhost"
    assert res.variables["API_KEY"].value == "sec-12345"
    assert res.variables["EMPTY_VAL"].is_empty is True
    assert "first line\nsecond line" in res.variables["MULTILINE"].value


def test_env_comparator(tmp_path: Path):
    tpl = tmp_path / ".env.example"
    tpl.write_text("PORT=3000\nSECRET_KEY=\nAPP_NAME=\n", encoding="utf-8")

    tgt = tmp_path / ".env"
    tgt.write_text("PORT=3000\nEXTRA_VAL=foo\n", encoding="utf-8")

    comp = compare_env_files(tpl, tgt)
    assert "SECRET_KEY" in comp.missing_in_target
    assert "APP_NAME" in comp.missing_in_target
    assert "EXTRA_VAL" in comp.extra_in_target
    assert "PORT" in comp.matching_keys


def test_schema_validation():
    # Valid port
    err = validate_variable("PORT", "8080", SchemaRule(type="port"))
    assert err is None

    # Invalid port
    err_bad_port = validate_variable("PORT", "99999", SchemaRule(type="port"))
    assert err_bad_port is not None
    assert "out of range" in err_bad_port.message

    # Boolean validation
    err_bool = validate_variable("DEBUG", "yes", SchemaRule(type="boolean"))
    assert err_bool is None
    err_bad_bool = validate_variable("DEBUG", "random_string", SchemaRule(type="boolean"))
    assert err_bad_bool is not None

    # Enum validation
    err_enum = validate_variable("ENV", "prod", SchemaRule(type="enum", allowed_values=["dev", "staging", "prod"]))
    assert err_enum is None
    err_bad_enum = validate_variable("ENV", "unknown", SchemaRule(type="enum", allowed_values=["dev", "staging", "prod"]))
    assert err_bad_enum is not None


def test_usage_scanner(tmp_path: Path):
    py_code = tmp_path / "server.py"
    py_code.write_text("import os\nport = os.getenv('PORT')\nhost = os.environ['DB_HOST']\n", encoding="utf-8")

    usages = scan_codebase_usages(tmp_path)
    var_names = {u.variable for u in usages}
    assert "PORT" in var_names
    assert "DB_HOST" in var_names


def test_secret_auditing(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("AWS_KEY=AKIA1234567890ABCDEF\n", encoding="utf-8")

    findings = audit_env_secrets(env_file)
    assert len(findings) == 1
    assert "AWS_KEY" in findings[0].message


def test_envcheck_cli(tmp_path: Path):
    runner = CliRunner()

    tpl = tmp_path / ".env.example"
    tpl.write_text("PORT=8000\n", encoding="utf-8")

    tgt = tmp_path / ".env"
    tgt.write_text("PORT=8000\n", encoding="utf-8")

    res = runner.invoke(main, [str(tmp_path), "--format", "json"])
    assert res.exit_code == 0
    assert "env-checker" in res.output

    # Compare command
    res_cmp = runner.invoke(main, ["compare", str(tpl), str(tgt)])
    assert res_cmp.exit_code == 0

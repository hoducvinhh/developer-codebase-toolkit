from toolkit_common.secrets.redactor import REDACTED_LABEL, SecretRedactor


def test_redact_aws_key():
    raw = "Deploy key is AKIA1234567890ABCDEF in production"
    redacted = SecretRedactor.redact_text(raw)
    assert "AKIA1234567890ABCDEF" not in redacted
    assert REDACTED_LABEL in redacted


def test_redact_connection_string():
    raw = "DATABASE_URL=postgres://user:super_secret_pwd@localhost:5432/db"
    redacted = SecretRedactor.redact_text(raw)
    assert "super_secret_pwd" not in redacted
    assert REDACTED_LABEL in redacted


def test_redact_dict():
    data = {
        "user": "alice",
        "api_key": "sec-12345-very-secret-token",
        "nested": {
            "password": "my_secret_password",
            "normal": "hello",
        },
    }
    cleaned = SecretRedactor.redact_dict(data)
    assert cleaned["user"] == "alice"
    assert cleaned["api_key"] == REDACTED_LABEL
    assert cleaned["nested"]["password"] == REDACTED_LABEL
    assert cleaned["nested"]["normal"] == "hello"

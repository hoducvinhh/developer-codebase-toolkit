import json
from pathlib import Path

from api_diff.cli import main
from api_diff.comparator import DiffResult
from api_diff.parser import OpenApiParser
from click.testing import CliRunner

OLD_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "Sample API", "version": "1.0.0"},
    "paths": {
        "/users": {
            "get": {
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"},
                                        "name": {"type": "string"},
                                    },
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"name": {"type": "string"}},
                            }
                        }
                    }
                },
                "responses": {"201": {"description": "Created"}},
            },
        },
        "/deprecated": {
            "get": {"responses": {"200": {"description": "OK"}}}
        },
    },
}

NEW_SPEC_BREAKING = {
    "openapi": "3.0.0",
    "info": {"title": "Sample API", "version": "2.0.0"},
    "paths": {
        "/users": {
            "get": {
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"},
                                        # "name" was removed -> BREAKING
                                    },
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["role"],  # added required field -> BREAKING
                                "properties": {
                                    "name": {"type": "string"},
                                    "role": {"type": "string"},
                                },
                            }
                        }
                    }
                },
                "responses": {"201": {"description": "Created"}},
            },
        },
        # /deprecated was removed -> BREAKING
    },
}


def test_parser_and_ref_resolution():
    doc = {
        "openapi": "3.0.0",
        "components": {
            "schemas": {
                "User": {"type": "object", "properties": {"id": {"type": "integer"}}}
            }
        },
        "paths": {
            "/user": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/User"}
                                }
                            }
                        }
                    }
                }
            }
        },
    }
    parser = OpenApiParser(doc)
    resolved_schema = parser.resolved_spec["paths"]["/user"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    assert resolved_schema["type"] == "object"
    assert "id" in resolved_schema["properties"]


def test_breaking_diff():
    res = DiffResult.compare(OLD_SPEC, NEW_SPEC_BREAKING)
    assert res.summary.breaking >= 2
    types = [c.change_type for c in res.changes]
    assert "ENDPOINT_REMOVED" in types
    assert "RESPONSE_PROPERTY_REMOVED" in types


def test_api_diff_cli(tmp_path: Path):
    old_file = tmp_path / "old.json"
    new_file = tmp_path / "new.json"
    old_file.write_text(json.dumps(OLD_SPEC), encoding="utf-8")
    new_file.write_text(json.dumps(NEW_SPEC_BREAKING), encoding="utf-8")

    runner = CliRunner()
    res = runner.invoke(main, [str(old_file), str(new_file), "--format", "json"])
    assert res.exit_code == 1  # ExitCode.BLOCKING_FINDINGS
    assert "api-diff" in res.output

    # With fail-on none, should return 0
    res_none = runner.invoke(main, [str(old_file), str(new_file), "--fail-on", "none"])
    assert res_none.exit_code == 0

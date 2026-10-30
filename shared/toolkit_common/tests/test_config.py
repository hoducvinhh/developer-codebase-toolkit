from pathlib import Path

from toolkit_common.config.loader import load_config_file


def test_load_yaml_and_json(tmp_path: Path):
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text("threshold: 10\nrules:\n  - rule_a\n  - rule_b\n", encoding="utf-8")

    json_file = tmp_path / "config.json"
    json_file.write_text('{"name": "test", "enabled": true}', encoding="utf-8")

    yaml_data = load_config_file(yaml_file)
    assert yaml_data["threshold"] == 10
    assert len(yaml_data["rules"]) == 2

    json_data = load_config_file(json_file)
    assert json_data["name"] == "test"
    assert json_data["enabled"] is True

"""Tests for YAML boolean key normalization."""

from pathlib import Path

import yaml

from trustline.contracts.loader import load_contract_raw


def test_yaml_on_key_normalized(tmp_path: Path) -> None:
    """YAML 1.1 parses bare ``on:`` as boolean True; loader should fix it."""
    path = tmp_path / "on_key.yaml"
    path.write_text(
        "join:\n  table: t\n  on: email\nalerts:\n  - on: retention_drop\n",
        encoding="utf-8",
    )
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert True in raw["join"]

    data = load_contract_raw(path)
    assert data["join"]["on"] == "email"
    assert data["alerts"][0]["on"] == "retention_drop"

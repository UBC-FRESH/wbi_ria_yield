from __future__ import annotations

from pathlib import Path

from femic.rebuild_spec import (
    load_rebuild_spec,
    validate_rebuild_spec_payload,
)


def test_load_rebuild_spec_requires_mapping_root(tmp_path: Path) -> None:
    spec = tmp_path / "bad.yaml"
    spec.write_text("- not-a-mapping\n", encoding="utf-8")
    try:
        load_rebuild_spec(spec)
    except ValueError as exc:
        assert "root must be a mapping" in str(exc)
    else:
        raise AssertionError("expected ValueError for non-mapping spec root")


def test_validate_rebuild_spec_payload_accepts_valid_minimal_payload() -> None:
    payload = {
        "schema_version": "1.0",
        "instance": {"case_id": "k3z"},
        "runtime": {},
        "steps": [
            {
                "step_id": "validate_case",
                "kind": "femic_command",
                "required": True,
                "depends_on": [],
            }
        ],
        "invariants": [
            {
                "invariant_id": "managed_area_sanity",
                "severity": "fatal",
                "metric": "accounts.list",
                "comparator": "contains",
                "target": "product.Yield.managed.PLC",
            }
        ],
    }
    errors = validate_rebuild_spec_payload(payload)
    assert not errors


def test_validate_rebuild_spec_payload_accepts_species_account_policy() -> None:
    payload = {
        "schema_version": "1.0",
        "instance": {"case_id": "k3z"},
        "runtime": {
            "species_account_policy": {
                "required_present": ["product.Yield.managed.PLC"],
                "expected_absent": ["product.Yield.managed.PL"],
            }
        },
        "steps": [
            {
                "step_id": "validate_case",
                "kind": "femic_command",
                "required": True,
                "depends_on": [],
            }
        ],
        "invariants": [
            {
                "invariant_id": "managed_area_sanity",
                "severity": "fatal",
                "metric": "managed_area_ha",
                "comparator": "gt",
                "target": 0,
            }
        ],
    }
    errors = validate_rebuild_spec_payload(payload)
    assert not errors


def test_validate_rebuild_spec_payload_emits_clear_errors() -> None:
    payload = {
        "schema_version": "0.9",
        "instance": {"case_id": ""},
        "runtime": {},
        "steps": [
            {
                "step_id": "s1",
                "kind": "bad-kind",
                "required": "yes",
                "depends_on": ["missing_step"],
            }
        ],
        "invariants": [
            {
                "invariant_id": "x",
                "severity": "critical",
                "metric": "m",
                "comparator": "bad",
                "target": 1,
            }
        ],
    }
    errors = validate_rebuild_spec_payload(payload)
    assert any("schema_version must be '1.0'" in msg for msg in errors)
    assert any("instance.case_id is required" in msg for msg in errors)
    assert any(".kind must be one of" in msg for msg in errors)
    assert any(".required must be boolean" in msg for msg in errors)
    assert any("depends_on references unknown step_id" in msg for msg in errors)
    assert any(".severity must be one of" in msg for msg in errors)
    assert any(".comparator must be one of" in msg for msg in errors)


def test_validate_rebuild_spec_payload_rejects_invalid_species_account_policy() -> None:
    payload = {
        "schema_version": "1.0",
        "instance": {"case_id": "k3z"},
        "runtime": {
            "species_account_policy": {
                "required_present": "not-a-list",
                "expected_absent": [""],
            }
        },
        "steps": [
            {
                "step_id": "validate_case",
                "kind": "femic_command",
                "required": True,
                "depends_on": [],
            }
        ],
        "invariants": [
            {
                "invariant_id": "managed_area_sanity",
                "severity": "fatal",
                "metric": "managed_area_ha",
                "comparator": "gt",
                "target": 0,
            }
        ],
    }
    errors = validate_rebuild_spec_payload(payload)
    assert any(
        "species_account_policy.required_present must be a list" in msg
        for msg in errors
    )
    assert any(
        "species_account_policy.expected_absent[0] must be a non-empty string" in msg
        for msg in errors
    )

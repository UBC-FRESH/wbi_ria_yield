"""Rebuild-spec loading and schema-style validation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


REBUILD_SPEC_REQUIRED_ROOT_KEYS = (
    "schema_version",
    "instance",
    "runtime",
    "steps",
    "invariants",
)
REBUILD_SPEC_REQUIRED_STEP_KEYS = ("step_id", "kind", "required")
REBUILD_SPEC_REQUIRED_INVARIANT_KEYS = (
    "invariant_id",
    "severity",
    "metric",
    "comparator",
    "target",
)
ALLOWED_STEP_KINDS = {"femic_command", "manual_boundary", "quality_gate"}
ALLOWED_INVARIANT_SEVERITIES = {"fatal", "warn"}
ALLOWED_INVARIANT_COMPARATORS = {
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
    "exists",
    "not_exists",
}


def load_rebuild_spec(spec_path: Path) -> dict[str, Any]:
    """Load a rebuild spec YAML file into a dictionary payload."""
    payload = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Rebuild spec root must be a mapping/object.")
    return payload


def validate_rebuild_spec_payload(payload: dict[str, Any]) -> list[str]:
    """Validate a rebuild spec payload and return human-readable errors."""
    errors: list[str] = []
    for key in REBUILD_SPEC_REQUIRED_ROOT_KEYS:
        if key not in payload:
            errors.append(f"Missing required root key: {key}")

    if payload.get("schema_version") != "1.0":
        errors.append(
            f"schema_version must be '1.0' (got {payload.get('schema_version')!r})"
        )

    instance = payload.get("instance")
    if not isinstance(instance, dict):
        errors.append("instance must be a mapping/object.")
    elif not str(instance.get("case_id", "")).strip():
        errors.append("instance.case_id is required and must be non-empty.")

    runtime = payload.get("runtime")
    if not isinstance(runtime, dict):
        errors.append("runtime must be a mapping/object.")

    steps = payload.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append("steps must be a non-empty list.")
    else:
        step_ids: list[str] = []
        for idx, step in enumerate(steps):
            where = f"steps[{idx}]"
            if not isinstance(step, dict):
                errors.append(f"{where} must be a mapping/object.")
                continue
            for key in REBUILD_SPEC_REQUIRED_STEP_KEYS:
                if key not in step:
                    errors.append(f"{where} missing required key: {key}")
            step_id = str(step.get("step_id", "")).strip()
            if not step_id:
                errors.append(f"{where}.step_id must be non-empty.")
            else:
                step_ids.append(step_id)
            kind = str(step.get("kind", "")).strip()
            if kind and kind not in ALLOWED_STEP_KINDS:
                errors.append(
                    f"{where}.kind must be one of {sorted(ALLOWED_STEP_KINDS)} "
                    f"(got {kind!r})"
                )
            depends_on = step.get("depends_on", [])
            if depends_on is not None and not isinstance(depends_on, list):
                errors.append(f"{where}.depends_on must be a list when present.")
            if "required" in step and not isinstance(step.get("required"), bool):
                errors.append(f"{where}.required must be boolean.")

        if len(step_ids) != len(set(step_ids)):
            errors.append("steps.step_id values must be unique.")
        step_id_set = set(step_ids)
        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            depends_on = step.get("depends_on", [])
            if not isinstance(depends_on, list):
                continue
            for dep in depends_on:
                dep_id = str(dep).strip()
                if dep_id and dep_id not in step_id_set:
                    errors.append(
                        f"steps[{idx}].depends_on references unknown step_id {dep_id!r}."
                    )

    invariants = payload.get("invariants")
    if not isinstance(invariants, list) or not invariants:
        errors.append("invariants must be a non-empty list.")
    else:
        invariant_ids: list[str] = []
        for idx, invariant in enumerate(invariants):
            where = f"invariants[{idx}]"
            if not isinstance(invariant, dict):
                errors.append(f"{where} must be a mapping/object.")
                continue
            for key in REBUILD_SPEC_REQUIRED_INVARIANT_KEYS:
                if key not in invariant:
                    errors.append(f"{where} missing required key: {key}")
            invariant_id = str(invariant.get("invariant_id", "")).strip()
            if not invariant_id:
                errors.append(f"{where}.invariant_id must be non-empty.")
            else:
                invariant_ids.append(invariant_id)
            severity = str(invariant.get("severity", "")).strip()
            if severity and severity not in ALLOWED_INVARIANT_SEVERITIES:
                errors.append(
                    f"{where}.severity must be one of "
                    f"{sorted(ALLOWED_INVARIANT_SEVERITIES)} (got {severity!r})"
                )
            comparator = str(invariant.get("comparator", "")).strip()
            if comparator and comparator not in ALLOWED_INVARIANT_COMPARATORS:
                errors.append(
                    f"{where}.comparator must be one of "
                    f"{sorted(ALLOWED_INVARIANT_COMPARATORS)} "
                    f"(got {comparator!r})"
                )
        if len(invariant_ids) != len(set(invariant_ids)):
            errors.append("invariants.invariant_id values must be unique.")

    return errors

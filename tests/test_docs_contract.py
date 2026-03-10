from __future__ import annotations

import csv
import json
from pathlib import Path

from typer.testing import CliRunner

from femic.cli.main import app

DOCS_ROOT = Path("docs")
GUIDES_ROOT = DOCS_ROOT / "guides"
COVERAGE_CSV = GUIDES_ROOT / "legacy_notebook_coverage.csv"

GUIDE_PAGES = [
    "pipeline-overview",
    "case-onboarding",
    "stage-00-data-prep",
    "stage-01a-vdyp-tipsy-input",
    "stage-01b-post-tipsy",
    "model-input-bundle-and-export",
    "diagnostics-playbook",
    "troubleshooting",
    "limitations-and-boundaries",
    "patchworks-wine-runtime",
    "ubc-vpn-license-connectivity",
    "legacy-traceability",
]

NOTEBOOKS = [
    Path("00_data-prep.ipynb"),
    Path("01a_run-tsa.ipynb"),
    Path("01b_run-tsa.ipynb"),
]

runner = CliRunner()


def _non_trivial_markdown_cells(path: Path) -> set[tuple[str, int]]:
    payload = json.loads(path.read_text())
    keys: set[tuple[str, int]] = set()
    for idx, cell in enumerate(payload.get("cells", [])):
        if cell.get("cell_type") != "markdown":
            continue
        text = " ".join("".join(cell.get("source", [])).split())
        if len(text) >= 10:
            keys.add((path.name, idx))
    return keys


def test_guides_pages_are_in_docs_tree() -> None:
    assert (DOCS_ROOT / "index.rst").exists()
    index_text = (DOCS_ROOT / "index.rst").read_text()
    assert "guides/index" in index_text

    guides_index = (GUIDES_ROOT / "index.rst").read_text()
    for slug in GUIDE_PAGES:
        page_path = GUIDES_ROOT / f"{slug}.rst"
        assert page_path.exists(), f"missing guide page: {page_path}"
        assert slug in guides_index, f"missing toctree entry for {slug}"


def test_legacy_notebook_coverage_matrix_is_complete() -> None:
    assert COVERAGE_CSV.exists(), "missing notebook coverage artifact"

    with COVERAGE_CSV.open(newline="") as fh:
        rows = list(csv.DictReader(fh))

    assert rows, "coverage CSV is empty"

    expected_keys: set[tuple[str, int]] = set()
    for notebook in NOTEBOOKS:
        expected_keys |= _non_trivial_markdown_cells(notebook)

    observed_keys: set[tuple[str, int]] = set()
    for row in rows:
        key = (row["notebook"], int(row["cell_index"]))
        observed_keys.add(key)
        assert row["classification"] in {
            "assumptions",
            "step intent",
            "interpretation guidance",
            "failure mode",
            "operator action",
        }
        assert row["status"] in {"mapped", "retired"}
        assert row["target_doc"].startswith("guides/")
        target_path = DOCS_ROOT / f"{row['target_doc']}.rst"
        assert target_path.exists(), f"target doc missing for row {key}: {target_path}"

    assert observed_keys == expected_keys


def test_cli_reference_mentions_current_high_value_options() -> None:
    cli_doc = (DOCS_ROOT / "reference" / "cli.rst").read_text()

    checks: list[tuple[list[str], list[str]]] = [
        (["run", "--help"], ["--run-config", "--run-id", "--log-dir", "--debug-rows"]),
        (
            ["prep", "validate-case", "--help"],
            ["--run-config", "--tipsy-config-dir", "--strict-warnings"],
        ),
        (
            ["vdyp", "report", "--help"],
            [
                "--max-curve-warnings",
                "--max-first-point-mismatches",
                "--max-curve-parse-errors",
                "--min-curve-events",
            ],
        ),
        (["tsa", "post-tipsy", "--help"], ["--tsa", "--run-id", "--log-dir"]),
        (
            ["export", "patchworks", "--help"],
            [
                "--bundle-dir",
                "--checkpoint",
                "--cc-transition-ifm",
                "--ifm-source-col",
                "--ifm-threshold",
                "--ifm-target-managed-share",
            ],
        ),
        (
            ["export", "release", "--help"],
            [
                "--case-id",
                "--patchworks-dir",
                "--woodstock-dir",
                "--strict",
                "--no-strict",
            ],
        ),
        (
            ["patchworks", "preflight", "--help"],
            ["--config"],
        ),
        (
            ["patchworks", "matrix-build", "--help"],
            ["--config", "--log-dir", "--run-id", "--interactive"],
        ),
        (
            ["patchworks", "build-blocks", "--help"],
            [
                "--config",
                "--model-dir",
                "--fragments-shp",
                "--topology-radius",
                "--with-topology",
                "--no-topology",
            ],
        ),
    ]

    for argv, options in checks:
        result = runner.invoke(app, argv)
        assert result.exit_code == 0, result.output
        for option in options:
            assert option in result.output, (
                f"CLI no longer exposes expected option {option}"
            )
            assert option in cli_doc, f"CLI docs missing option {option}"


def test_case_onboarding_templates_exist() -> None:
    assert Path("config/run_profile.case_template.yaml").exists()
    assert Path("config/tipsy/template.case.yaml").exists()

from __future__ import annotations

import csv
import json
from pathlib import Path

from typer.testing import CliRunner

from femic.cli.main import app

DOCS_ROOT = Path("docs")
GUIDES_ROOT = DOCS_ROOT / "guides"
SAMPLE_MODELS_ROOT = DOCS_ROOT / "sample-models"
COVERAGE_CSV = GUIDES_ROOT / "legacy_notebook_coverage.csv"

GUIDE_PAGES = [
    "pipeline-overview",
    "deployment-instances",
    "data-access-inventory",
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
SAMPLE_MODEL_PAGES = [
    "k3z",
    "k3z-metadata-lineage",
]

NOTEBOOKS = [
    Path("00_data-prep.ipynb"),
    Path("01a_run-tsa.ipynb"),
    Path("01b_run-tsa.ipynb"),
]
LEGACY_SLUG = "wbi_ria_yield"

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
        (
            ["run", "--help"],
            [
                "--run-config",
                "--run-id",
                "--log-dir",
                "--debug-rows",
                "--instance-root",
            ],
        ),
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
                "--instance-root",
            ],
        ),
        (
            ["instance", "init", "--help"],
            [
                "--instance-root",
                "--overwrite",
                "--download-bc-vri",
                "--no-download-bc-vri",
                "--yes",
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


def test_case_onboarding_guide_keeps_template_and_preflight_links() -> None:
    guide_text = (GUIDES_ROOT / "case-onboarding.rst").read_text()
    assert "config/run_profile.case_template.yaml" in guide_text
    assert "config/tipsy/template.case.yaml" in guide_text
    assert "python -m femic prep validate-case" in guide_text


def test_sample_model_pages_are_in_docs_tree() -> None:
    assert (DOCS_ROOT / "index.rst").exists()
    index_text = (DOCS_ROOT / "index.rst").read_text()
    assert "sample-models/index" in index_text

    sample_models_index = (SAMPLE_MODELS_ROOT / "index.rst").read_text()
    for slug in SAMPLE_MODEL_PAGES:
        page_path = SAMPLE_MODELS_ROOT / f"{slug}.rst"
        assert page_path.exists(), f"missing sample-model page: {page_path}"
        assert slug in sample_models_index, f"missing toctree entry for {slug}"


def test_k3z_sample_model_docs_keep_required_sections() -> None:
    k3z_text = (SAMPLE_MODELS_ROOT / "k3z.rst").read_text()
    required_k3z_sections = [
        "Purpose and Scope",
        "Model Anatomy",
        "Build and Rebuild Workflow",
        "Parameter Risk and Suggested Ranges",
        "Edit Policy: Safe vs Generated",
        "Backup and Recovery Conventions",
        "Scenario Comparison Guidance",
        "Release Readiness Checklist",
        "Troubleshooting",
    ]
    for heading in required_k3z_sections:
        assert heading in k3z_text, f"k3z.rst missing required section: {heading}"

    lineage_text = (SAMPLE_MODELS_ROOT / "k3z-metadata-lineage.rst").read_text()
    required_lineage_sections = [
        "Inventory: Upstream Sources -> Model Artifacts",
        "Build-Lineage Chain",
        "Provenance Versioning Policy",
        "Acceptance Checklist for Lineage Updates",
    ]
    for heading in required_lineage_sections:
        assert heading in lineage_text, (
            f"k3z-metadata-lineage.rst missing required section: {heading}"
        )


def test_legacy_traceability_docs_include_notebook_cleanup_policy() -> None:
    traceability_text = (GUIDES_ROOT / "legacy-traceability.rst").read_text()
    assert "Notebook Output Cleanup Policy" in traceability_text
    assert "jupyter nbconvert --clear-output --inplace" in traceability_text


def test_legacy_slug_references_are_limited_to_audit_trail_files() -> None:
    allowed_paths = {
        Path("ROADMAP.md"),
        Path("CHANGE_LOG.md"),
    }
    candidate_files = [
        Path("README.md"),
        Path("CITATION.cff"),
        Path("pyproject.toml"),
        Path(".github/workflows/docs-pages.yml"),
    ]
    allowed_suffixes = {
        ".py",
        ".rst",
        ".md",
        ".yaml",
        ".yml",
        ".toml",
        ".cff",
        ".json",
        ".txt",
    }
    for root in (Path("src"), Path("docs"), Path("config")):
        candidate_files.extend(
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in allowed_suffixes
        )

    offenders: list[str] = []
    for path in candidate_files:
        if path in allowed_paths:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if LEGACY_SLUG in text:
            offenders.append(str(path))

    assert not offenders, "legacy slug appears outside audit-trail files: " + ", ".join(
        offenders
    )

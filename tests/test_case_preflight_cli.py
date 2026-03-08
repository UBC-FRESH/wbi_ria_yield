from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from typer.testing import CliRunner

from femic.cli import main as cli_main
from femic.cli.main import app


runner = CliRunner()


def _write_profile(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")


def _write_min_tipsy_cfg(path: Path, code: str) -> None:
    path.write_text(
        "schema_version: 1\n"
        f"tsa_code: '{code}'\n"
        "rules:\n"
        "  - id: r\n"
        "    when: {}\n"
        "    assign:\n"
        "      e: {}\n"
        "      f: {}\n",
        encoding="utf-8",
    )


def _mock_external_paths(root: Path) -> SimpleNamespace:
    vri = root / "vri.gdb"
    vdyp = root / "vdyp.gdb"
    tsa = root / "tsa.gdb"
    siteprod = root / "siteprod.gdb"
    for path in (vri, vdyp, tsa, siteprod):
        path.touch()
    return SimpleNamespace(
        vri_vclr1p_path=vri,
        vdyp_input_pandl_path=vdyp,
        tsa_boundaries_path=tsa,
        site_prod_bc_gdb_path=siteprod,
    )


def test_prep_validate_case_passes_with_tsa_profile(
    tmp_path: Path, monkeypatch
) -> None:
    profile = tmp_path / "run_profile.yaml"
    _write_profile(
        profile,
        "selection:\n"
        "  tsa: ['08']\n"
        "run:\n"
        f"  log_dir: '{(tmp_path / 'logs').as_posix()}'\n",
    )

    cfg_dir = tmp_path / "tipsy"
    cfg_dir.mkdir()
    _write_min_tipsy_cfg(cfg_dir / "tsa08.yaml", "08")

    monkeypatch.setattr(cli_main, "_preflight_checks", lambda *, resume: None)
    monkeypatch.setattr(
        cli_main,
        "resolve_legacy_external_data_paths",
        lambda **_: _mock_external_paths(tmp_path),
    )

    result = runner.invoke(
        app,
        [
            "prep",
            "validate-case",
            "--run-config",
            str(profile),
            "--tipsy-config-dir",
            str(cfg_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Case preflight passed" in result.stdout
    assert "targets=[08]" in result.stdout


def test_prep_validate_case_fails_when_tipsy_config_missing(
    tmp_path: Path, monkeypatch
) -> None:
    profile = tmp_path / "run_profile.yaml"
    _write_profile(
        profile,
        "selection:\n"
        "  tsa: ['08']\n"
        "run:\n"
        f"  log_dir: '{(tmp_path / 'logs').as_posix()}'\n",
    )

    cfg_dir = tmp_path / "tipsy"
    cfg_dir.mkdir()

    monkeypatch.setattr(cli_main, "_preflight_checks", lambda *, resume: None)
    monkeypatch.setattr(
        cli_main,
        "resolve_legacy_external_data_paths",
        lambda **_: _mock_external_paths(tmp_path),
    )

    result = runner.invoke(
        app,
        [
            "prep",
            "validate-case",
            "--run-config",
            str(profile),
            "--tipsy-config-dir",
            str(cfg_dir),
        ],
    )

    assert result.exit_code == 1
    assert "Missing TIPSY config for 08" in result.stdout


def test_prep_validate_case_fails_when_boundary_code_missing(
    tmp_path: Path, monkeypatch
) -> None:
    boundary = tmp_path / "boundary.shp"
    boundary.touch()
    profile = tmp_path / "run_profile.yaml"
    _write_profile(
        profile,
        "selection:\n"
        f"  boundary_path: '{boundary.as_posix()}'\n"
        "run:\n"
        f"  log_dir: '{(tmp_path / 'logs').as_posix()}'\n",
    )

    cfg_dir = tmp_path / "tipsy"
    cfg_dir.mkdir()

    monkeypatch.setattr(cli_main, "_preflight_checks", lambda *, resume: None)
    monkeypatch.setattr(
        cli_main,
        "resolve_legacy_external_data_paths",
        lambda **_: _mock_external_paths(tmp_path),
    )

    result = runner.invoke(
        app,
        [
            "prep",
            "validate-case",
            "--run-config",
            str(profile),
            "--tipsy-config-dir",
            str(cfg_dir),
        ],
    )

    assert result.exit_code == 1
    assert "selection.boundary_code is required" in result.stdout


def test_prep_validate_case_strict_warnings_fails(tmp_path: Path, monkeypatch) -> None:
    profile = tmp_path / "run_profile.yaml"
    # Intentionally point log_dir to a non-existent path to trigger warning.
    _write_profile(
        profile,
        "selection:\n"
        "  tsa: ['08']\n"
        "run:\n"
        f"  log_dir: '{(tmp_path / 'does_not_exist' / 'logs').as_posix()}'\n",
    )

    cfg_dir = tmp_path / "tipsy"
    cfg_dir.mkdir()
    _write_min_tipsy_cfg(cfg_dir / "tsa08.yaml", "08")

    monkeypatch.setattr(cli_main, "_preflight_checks", lambda *, resume: None)
    monkeypatch.setattr(
        cli_main,
        "resolve_legacy_external_data_paths",
        lambda **_: _mock_external_paths(tmp_path),
    )

    result = runner.invoke(
        app,
        [
            "prep",
            "validate-case",
            "--run-config",
            str(profile),
            "--tipsy-config-dir",
            str(cfg_dir),
            "--strict-warnings",
        ],
    )

    assert result.exit_code == 1
    assert "strict warning mode enabled" in result.stdout

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from femic.patchworks_runtime import (
    PatchworksConfigError,
    build_appchooser_command_string,
    build_matrix_builder_command_string,
    load_patchworks_runtime_config,
    parse_license_server,
    run_patchworks_command,
    run_patchworks_preflight,
    to_wine_windows_path,
)


def _write_runtime_config(tmp_path: Path) -> Path:
    cfg = tmp_path / "patchworks.runtime.yaml"
    cfg.write_text(
        "\n".join(
            [
                "patchworks:",
                "  jar_path: patchworks/patchworks.jar",
                "  wine_prefix: null",
                "  license_env: SPS_LICENSE_SERVER",
                "  license_value: frst424@auth.spatial.ca",
                "  spshome: Z:\\Patchworks",
                "matrix_builder:",
                "  fragments_path: data/fragments.dbf",
                "  output_dir: output/tracks",
                "  forestmodel_xml_path: output/forestmodel.xml",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return cfg


def test_load_patchworks_runtime_config_resolves_relative_paths(tmp_path: Path) -> None:
    cfg_path = _write_runtime_config(tmp_path)
    cfg = load_patchworks_runtime_config(cfg_path)

    assert cfg.jar_path == (tmp_path / "patchworks/patchworks.jar").resolve()
    assert cfg.fragments_path == (tmp_path / "data/fragments.dbf").resolve()
    assert cfg.matrix_output_dir == (tmp_path / "output/tracks").resolve()
    assert cfg.forestmodel_xml_path == (tmp_path / "output/forestmodel.xml").resolve()


def test_load_patchworks_runtime_config_handles_parent_relative_paths(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    cfg_dir = repo_root / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    (repo_root / "reference/Patchworks").mkdir(parents=True, exist_ok=True)
    (repo_root / "reference/Patchworks/patchworks.jar").touch()
    (repo_root / "output/patchworks_k3z_validated/fragments").mkdir(
        parents=True, exist_ok=True
    )
    (repo_root / "output/patchworks_k3z_validated/fragments/fragments.dbf").touch()
    (repo_root / "output/patchworks_k3z_validated/forestmodel.xml").touch()

    cfg_path = cfg_dir / "patchworks.runtime.yaml"
    cfg_path.write_text(
        "\n".join(
            [
                "patchworks:",
                "  jar_path: ../reference/Patchworks/patchworks.jar",
                "  license_env: SPS_LICENSE_SERVER",
                "  license_value: frst424@auth.spatial.ca",
                "  spshome: Z:\\Patchworks",
                "matrix_builder:",
                "  fragments_path: ../output/patchworks_k3z_validated/fragments/fragments.dbf",
                "  output_dir: ../output/patchworks_k3z_validated/tracks",
                "  forestmodel_xml_path: ../output/patchworks_k3z_validated/forestmodel.xml",
                "",
            ]
        ),
        encoding="utf-8",
    )
    cfg = load_patchworks_runtime_config(cfg_path)
    assert cfg.jar_path == (repo_root / "reference/Patchworks/patchworks.jar").resolve()
    assert (
        cfg.fragments_path
        == (
            repo_root / "output/patchworks_k3z_validated/fragments/fragments.dbf"
        ).resolve()
    )


def test_parse_license_server_requires_user_host_format() -> None:
    assert parse_license_server("frst424@auth.spatial.ca") == (
        "frst424",
        "auth.spatial.ca",
    )
    with pytest.raises(PatchworksConfigError):
        parse_license_server("auth.spatial.ca")


def test_to_wine_windows_path_maps_posix(tmp_path: Path) -> None:
    path = (tmp_path / "a b/c.txt").resolve()
    path.parent.mkdir(parents=True)
    path.touch()
    mapped = to_wine_windows_path(path)
    assert mapped.startswith("Z:\\")
    assert "a b" in mapped


def test_build_matrix_builder_command_string_contains_expected_args(
    tmp_path: Path,
) -> None:
    cfg_path = _write_runtime_config(tmp_path)
    cfg = load_patchworks_runtime_config(cfg_path)
    cmd = build_matrix_builder_command_string(cfg)
    assert "ca.spatial.tracks.builder.Process" in cmd
    assert "fragments.dbf" in cmd
    assert "forestmodel.xml" in cmd


def test_build_appchooser_command_string_points_to_patchworks_jar(
    tmp_path: Path,
) -> None:
    cfg_path = _write_runtime_config(tmp_path)
    cfg = load_patchworks_runtime_config(cfg_path)
    cmd = build_appchooser_command_string(cfg)
    assert "java -Djava.library.path=" in cmd
    assert "-jar patchworks.jar" in cmd


def test_run_patchworks_preflight_reports_missing_assets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg_path = _write_runtime_config(tmp_path)
    cfg = load_patchworks_runtime_config(cfg_path)

    monkeypatch.setattr("femic.patchworks_runtime.find_wine_executable", lambda: None)

    result = run_patchworks_preflight(config=cfg)
    assert not result.ok
    assert any("wine64/wine not found" in msg for msg in result.errors)
    assert any("Patchworks jar not found" in msg for msg in result.errors)


def test_load_patchworks_runtime_config_requires_spshome(tmp_path: Path) -> None:
    cfg = tmp_path / "patchworks.runtime.yaml"
    cfg.write_text(
        "\n".join(
            [
                "patchworks:",
                "  jar_path: patchworks/patchworks.jar",
                "  wine_prefix: null",
                "  license_env: SPS_LICENSE_SERVER",
                "  license_value: frst424@auth.spatial.ca",
                "matrix_builder:",
                "  fragments_path: data/fragments.dbf",
                "  output_dir: output/tracks",
                "  forestmodel_xml_path: output/forestmodel.xml",
                "",
            ]
        ),
        encoding="utf-8",
    )
    with pytest.raises(PatchworksConfigError, match="Missing Patchworks install home"):
        load_patchworks_runtime_config(cfg)


def test_run_patchworks_command_writes_logs_and_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg_path = _write_runtime_config(tmp_path)
    cfg = load_patchworks_runtime_config(cfg_path)

    cfg.jar_path.parent.mkdir(parents=True, exist_ok=True)
    cfg.jar_path.touch()
    cfg.fragments_path.parent.mkdir(parents=True, exist_ok=True)
    cfg.fragments_path.touch()
    cfg.forestmodel_xml_path.parent.mkdir(parents=True, exist_ok=True)
    cfg.forestmodel_xml_path.touch()
    cfg.matrix_output_dir.mkdir(parents=True, exist_ok=True)
    (cfg.matrix_output_dir / "tracks.bin").write_text("ok", encoding="utf-8")

    monkeypatch.setattr(
        "femic.patchworks_runtime.find_wine_executable", lambda: "/usr/bin/wine64"
    )

    observed_env: dict[str, str] = {}

    def _fake_subprocess_run(*_args, **_kwargs):
        nonlocal observed_env
        observed_env = dict(_kwargs.get("env", {}))
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr("femic.patchworks_runtime.subprocess.run", _fake_subprocess_run)

    result = run_patchworks_command(
        config=cfg,
        interactive=False,
        log_dir=tmp_path / "logs",
        run_id="pwtest",
    )

    assert result.returncode == 0
    assert result.stdout_log_path.exists()
    assert result.stderr_log_path.exists()
    assert result.manifest_path.exists()

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["run_id"] == "pwtest"
    assert manifest["returncode"] == 0
    assert "ca.spatial.tracks.builder.Process" in manifest["command_string"]
    assert manifest["runtime"]["spshome"] == "Z:\\Patchworks"
    assert observed_env["SPS_LICENSE_SERVER"] == "frst424@auth.spatial.ca"
    assert observed_env["SPSHOME"] == "Z:\\Patchworks"
    assert not result.failures


def test_run_patchworks_command_fails_on_fatal_stderr_signature(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg_path = _write_runtime_config(tmp_path)
    cfg = load_patchworks_runtime_config(cfg_path)
    cfg.jar_path.parent.mkdir(parents=True, exist_ok=True)
    cfg.jar_path.touch()
    cfg.fragments_path.parent.mkdir(parents=True, exist_ok=True)
    cfg.fragments_path.touch()
    cfg.forestmodel_xml_path.parent.mkdir(parents=True, exist_ok=True)
    cfg.forestmodel_xml_path.touch()
    cfg.matrix_output_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(
        "femic.patchworks_runtime.find_wine_executable", lambda: "/usr/bin/wine64"
    )

    def _fake_subprocess_run(*_args, **_kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout="",
            stderr="Not licensed or no connection to license server",
        )

    monkeypatch.setattr("femic.patchworks_runtime.subprocess.run", _fake_subprocess_run)

    result = run_patchworks_command(
        config=cfg, interactive=False, log_dir=tmp_path / "logs", run_id="pwfatal"
    )
    assert result.returncode == 1
    assert any("fatal stderr signatures detected" in x for x in result.failures)

from __future__ import annotations

import builtins
from pathlib import Path
from types import SimpleNamespace

import pytest
import typer

from femic.cli import main as cli_main


def _set_cli_repo_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    fake_module_path = repo_root / "src" / "femic" / "cli" / "main.py"
    fake_module_path.parent.mkdir(parents=True, exist_ok=True)
    fake_module_path.write_text("# fake module path for preflight tests\n")
    monkeypatch.setattr(cli_main, "__file__", str(fake_module_path))
    return repo_root


def _create_preflight_required_layout(repo_root: Path) -> None:
    data_root = repo_root / "data"
    data_root.mkdir(parents=True, exist_ok=True)
    (data_root / "tsa_boundaries.feather").touch()
    (data_root / "ria_vri_vclr1p_checkpoint1.feather").touch()
    (data_root / "tipsy_params_columns").touch()
    (data_root / "vdyp_ply.feather").touch()
    (data_root / "vdyp_lyr.feather").touch()
    (data_root / "vdyp_results.pkl").touch()

    (repo_root / "ria_maptiles.csv").touch()

    vdyp_cfg = repo_root / "vdyp_io" / "VDYP_CFG"
    vdyp_cfg.mkdir(parents=True, exist_ok=True)

    vdyp_exe = repo_root / "VDYP7" / "VDYP7" / "VDYP7Console.exe"
    vdyp_exe.parent.mkdir(parents=True, exist_ok=True)
    vdyp_exe.touch()


def test_enable_rich_tracebacks_ignores_missing_rich(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import = builtins.__import__

    def _patched_import(
        name: str,
        globals: object = None,
        locals: object = None,
        fromlist: object = (),
        level: int = 0,
    ) -> object:
        if name == "rich.traceback":
            raise ModuleNotFoundError("rich not installed")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _patched_import)
    cli_main._enable_rich_tracebacks()


def test_enable_rich_tracebacks_unexpected_import_error_propagates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import = builtins.__import__

    def _patched_import(
        name: str,
        globals: object = None,
        locals: object = None,
        fromlist: object = (),
        level: int = 0,
    ) -> object:
        if name == "rich.traceback":
            raise ZeroDivisionError("unexpected")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _patched_import)
    with pytest.raises(ZeroDivisionError, match="unexpected"):
        cli_main._enable_rich_tracebacks()


def test_preflight_checks_exit_when_data_root_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _set_cli_repo_root(monkeypatch, tmp_path)
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)
    monkeypatch.setattr(cli_main.shutil, "which", lambda _: "/usr/bin/wine")

    with pytest.raises(typer.Exit) as exc_info:
        cli_main._preflight_checks(resume=False)

    assert exc_info.value.exit_code == 1
    assert any("Missing data directory" in msg for msg in messages)


def test_preflight_checks_resume_warns_when_wine_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo_root = _set_cli_repo_root(monkeypatch, tmp_path)
    _create_preflight_required_layout(repo_root)

    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)
    monkeypatch.setattr(cli_main.shutil, "which", lambda _: None)

    cli_main._preflight_checks(resume=True)

    assert any("wine not found on PATH" in msg for msg in messages)
    assert not any("[red]Error:" in msg for msg in messages)


def test_preflight_checks_fails_for_specific_missing_required_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo_root = _set_cli_repo_root(monkeypatch, tmp_path)
    _create_preflight_required_layout(repo_root)
    missing_required = repo_root / "data" / "tipsy_params_columns"
    missing_required.unlink()

    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)
    monkeypatch.setattr(cli_main.shutil, "which", lambda _: "/usr/bin/wine")

    with pytest.raises(typer.Exit) as exc_info:
        cli_main._preflight_checks(resume=False)

    assert exc_info.value.exit_code == 1
    error_messages = [msg for msg in messages if "[red]Error:" in msg]
    assert len(error_messages) == 1
    assert "Missing required file" in error_messages[0]
    assert str(missing_required) in error_messages[0]


def test_run_all_exits_on_invalid_run_config(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    cfg_path = tmp_path / "bad.json"
    cfg_path.write_text("[]", encoding="utf-8")
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)

    with pytest.raises(typer.Exit) as exc_info:
        cli_main.run_all(
            data_root=Path("data"),
            output_root=Path("outputs"),
            tsa=None,
            resume=False,
            dry_run=False,
            verbose=False,
            skip_checks=False,
            debug_rows=None,
            run_id=None,
            log_dir=Path("vdyp_io/logs"),
            run_config=cfg_path,
        )

    assert exc_info.value.exit_code == 1
    assert any("Invalid run config" in msg for msg in messages)


def test_run_all_uses_profile_dry_run_and_profile_defaults(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    cfg_path = tmp_path / "run_profile.yaml"
    cfg_path.write_text(
        "\n".join(
            [
                "selection:",
                "  tsa: ['16']",
                "modes:",
                "  resume: true",
                "  dry_run: true",
                "  debug_rows: 12",
                "run:",
                "  run_id: cfg-run",
                "  log_dir: vdyp_io/custom_logs",
                "",
            ]
        ),
        encoding="utf-8",
    )
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)

    with pytest.raises(typer.Exit) as exc_info:
        cli_main.run_all(
            data_root=Path("data"),
            output_root=Path("outputs"),
            tsa=None,
            resume=False,
            dry_run=False,
            verbose=False,
            skip_checks=False,
            debug_rows=None,
            run_id=None,
            log_dir=Path("vdyp_io/logs"),
            run_config=cfg_path,
        )

    assert exc_info.value.exit_code == 0
    assert any("Dry run" in msg for msg in messages)
    assert any("tsa=['16']" in msg for msg in messages)
    assert any("resume=True" in msg for msg in messages)
    assert any("debug_rows=12" in msg for msg in messages)
    assert any("run_id=cfg-run" in msg for msg in messages)


def test_tsa_post_tipsy_requires_tsa(monkeypatch: pytest.MonkeyPatch) -> None:
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)

    with pytest.raises(typer.Exit) as exc_info:
        cli_main.tsa_post_tipsy(tsa=None, verbose=False)

    assert exc_info.value.exit_code == 1
    assert any("Provide at least one TSA" in msg for msg in messages)


def test_tsa_post_tipsy_calls_workflow(monkeypatch: pytest.MonkeyPatch) -> None:
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)
    called: dict[str, object] = {}

    def _fake_run_post_tipsy_bundle_with_manifest(
        *, tsa_list, run_id, log_dir, message_fn
    ):
        called["tsa_list"] = tsa_list
        called["run_id"] = run_id
        called["log_dir"] = log_dir
        message_fn("fake-progress")
        return SimpleNamespace(
            manifest_path=Path("vdyp_io/logs/run_manifest-post_tipsy_test.json"),
            result=SimpleNamespace(
                tsa_list=tsa_list,
                au_rows=30,
                curve_rows=60,
                curve_points_rows=9000,
                au_table_path=Path("data/model_input_bundle/au_table.csv"),
                curve_table_path=Path("data/model_input_bundle/curve_table.csv"),
                curve_points_table_path=Path(
                    "data/model_input_bundle/curve_points_table.csv"
                ),
            ),
        )

    monkeypatch.setattr(
        cli_main,
        "run_post_tipsy_bundle_with_manifest",
        _fake_run_post_tipsy_bundle_with_manifest,
    )

    cli_main.tsa_post_tipsy(
        tsa=["29"],
        verbose=True,
        run_id="post_tipsy_test",
        log_dir=Path("vdyp_io/logs"),
    )

    assert called["tsa_list"] == ["29"]
    assert called["run_id"] == "post_tipsy_test"
    assert called["log_dir"] == Path("vdyp_io/logs")
    assert any("post-tipsy completed" in msg for msg in messages)
    assert any("Run manifest:" in msg for msg in messages)
    assert any("fake-progress" in msg for msg in messages)


def test_export_patchworks_requires_tsa(monkeypatch: pytest.MonkeyPatch) -> None:
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)

    with pytest.raises(typer.Exit) as exc_info:
        cli_main.export_patchworks(tsa=None)

    assert exc_info.value.exit_code == 1
    assert any("Provide at least one TSA" in msg for msg in messages)


def test_export_patchworks_calls_exporter(monkeypatch: pytest.MonkeyPatch) -> None:
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)
    called: dict[str, object] = {}

    def _fake_export_patchworks_package(
        *,
        bundle_dir,
        checkpoint_path,
        output_dir,
        tsa_list,
        start_year,
        horizon_years,
        cc_min_age,
        cc_max_age,
        fragments_crs,
    ):
        called.update(
            {
                "bundle_dir": bundle_dir,
                "checkpoint_path": checkpoint_path,
                "output_dir": output_dir,
                "tsa_list": tsa_list,
                "start_year": start_year,
                "horizon_years": horizon_years,
                "cc_min_age": cc_min_age,
                "cc_max_age": cc_max_age,
                "fragments_crs": fragments_crs,
            }
        )
        return SimpleNamespace(
            forestmodel_xml_path=Path("output/patchworks/forestmodel.xml"),
            fragments_shapefile_path=Path("output/patchworks/fragments/fragments.shp"),
            tsa_list=tsa_list,
            au_count=12,
            fragment_count=218,
            curve_count=48,
        )

    monkeypatch.setattr(
        cli_main, "export_patchworks_package", _fake_export_patchworks_package
    )

    cli_main.export_patchworks(
        tsa=["k3z"],
        bundle_dir=Path("data/model_input_bundle"),
        checkpoint=Path("data/ria_vri_vclr1p_checkpoint7.feather"),
        output_dir=Path("output/patchworks"),
        start_year=2026,
        horizon_years=300,
        cc_min_age=0,
        cc_max_age=500,
        fragments_crs="EPSG:3005",
    )

    assert called["tsa_list"] == ["k3z"]
    assert called["cc_max_age"] == 500
    assert any("patchworks export completed" in msg for msg in messages)


def test_export_woodstock_requires_tsa(monkeypatch: pytest.MonkeyPatch) -> None:
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)

    with pytest.raises(typer.Exit) as exc_info:
        cli_main.export_woodstock(tsa=None)

    assert exc_info.value.exit_code == 1
    assert any("Provide at least one TSA" in msg for msg in messages)


def test_export_woodstock_calls_exporter(monkeypatch: pytest.MonkeyPatch) -> None:
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)
    called: dict[str, object] = {}

    def _fake_export_woodstock_package(
        *,
        bundle_dir,
        checkpoint_path,
        output_dir,
        tsa_list,
        fragments_crs,
    ):
        called.update(
            {
                "bundle_dir": bundle_dir,
                "checkpoint_path": checkpoint_path,
                "output_dir": output_dir,
                "tsa_list": tsa_list,
                "fragments_crs": fragments_crs,
            }
        )
        return SimpleNamespace(
            yields_csv_path=Path("output/woodstock/woodstock_yields.csv"),
            areas_csv_path=Path("output/woodstock/woodstock_areas.csv"),
            tsa_list=tsa_list,
            yield_rows=1234,
            area_rows=567,
        )

    monkeypatch.setattr(
        cli_main, "export_woodstock_package", _fake_export_woodstock_package
    )

    cli_main.export_woodstock(
        tsa=["k3z"],
        bundle_dir=Path("data/model_input_bundle"),
        checkpoint=Path("data/ria_vri_vclr1p_checkpoint7.feather"),
        output_dir=Path("output/woodstock"),
        fragments_crs="EPSG:3005",
    )

    assert called["tsa_list"] == ["k3z"]
    assert called["fragments_crs"] == "EPSG:3005"
    assert any("woodstock export completed" in msg for msg in messages)

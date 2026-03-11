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
        cli_main._preflight_checks(
            resume=False,
            instance_context=SimpleNamespace(root=tmp_path / "repo"),
        )

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

    cli_main._preflight_checks(
        resume=True,
        instance_context=SimpleNamespace(root=repo_root),
    )

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
        cli_main._preflight_checks(
            resume=False,
            instance_context=SimpleNamespace(root=repo_root),
        )

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
        cli_main.tsa_post_tipsy(
            tsa=None,
            verbose=False,
            run_id=None,
            log_dir=Path("vdyp_io/logs"),
            run_config=None,
        )

    assert exc_info.value.exit_code == 1
    assert any("Provide at least one TSA" in msg for msg in messages)


def test_tsa_post_tipsy_calls_workflow(monkeypatch: pytest.MonkeyPatch) -> None:
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)
    called: dict[str, object] = {}

    def _fake_run_post_tipsy_bundle_with_manifest(
        *,
        tsa_list,
        run_id,
        log_dir,
        repo_root,
        data_root,
        message_fn,
        managed_curve_mode,
        managed_curve_x_scale,
        managed_curve_y_scale,
        managed_curve_truncate_at_culm,
        managed_curve_max_age,
    ):
        called["tsa_list"] = tsa_list
        called["run_id"] = run_id
        called["log_dir"] = log_dir
        called["repo_root"] = repo_root
        called["data_root"] = data_root
        called["managed_curve_mode"] = managed_curve_mode
        called["managed_curve_x_scale"] = managed_curve_x_scale
        called["managed_curve_y_scale"] = managed_curve_y_scale
        called["managed_curve_truncate_at_culm"] = managed_curve_truncate_at_culm
        called["managed_curve_max_age"] = managed_curve_max_age
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
        run_config=None,
    )

    assert called["tsa_list"] == ["29"]
    assert called["run_id"] == "post_tipsy_test"
    assert Path(called["log_dir"]).as_posix().endswith("vdyp_io/logs")
    assert isinstance(called["repo_root"], Path)
    assert isinstance(called["data_root"], Path)
    assert called["managed_curve_mode"] is None
    assert called["managed_curve_x_scale"] is None
    assert called["managed_curve_y_scale"] is None
    assert called["managed_curve_truncate_at_culm"] is None
    assert called["managed_curve_max_age"] is None
    assert any("post-tipsy completed" in msg for msg in messages)
    assert any("Run manifest:" in msg for msg in messages)
    assert any("fake-progress" in msg for msg in messages)


def test_tsa_post_tipsy_uses_run_config_managed_curve_options(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)
    called: dict[str, object] = {}

    cfg_path = tmp_path / "run_profile.k3z.yaml"
    cfg_path.write_text(
        "\n".join(
            [
                "selection:",
                "  tsa: ['k3z']",
                "modes:",
                "  managed_curve_mode: vdyp_transform",
                "  managed_curve_x_scale: 0.8",
                "  managed_curve_y_scale: 1.2",
                "  managed_curve_truncate_at_culm: true",
                "  managed_curve_max_age: 300",
                "run:",
                "  run_id: cfg_post_tipsy",
            ]
        ),
        encoding="utf-8",
    )

    def _fake_run_post_tipsy_bundle_with_manifest(**kwargs):
        called.update(kwargs)
        return SimpleNamespace(
            manifest_path=Path("vdyp_io/logs/run_manifest-cfg_post_tipsy.json"),
            result=SimpleNamespace(
                tsa_list=kwargs["tsa_list"],
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
        tsa=None,
        verbose=False,
        run_id=None,
        log_dir=Path("vdyp_io/logs"),
        run_config=cfg_path,
    )

    assert called["tsa_list"] == ["k3z"]
    assert called["run_id"] == "cfg_post_tipsy"
    assert called["managed_curve_mode"] == "vdyp_transform"
    assert called["managed_curve_x_scale"] == 0.8
    assert called["managed_curve_y_scale"] == 1.2
    assert called["managed_curve_truncate_at_culm"] is True
    assert called["managed_curve_max_age"] == 300


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
        cc_transition_ifm,
        fragments_crs,
        ifm_source_col,
        ifm_threshold,
        ifm_target_managed_share,
        seral_stage_config_path,
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
                "cc_transition_ifm": cc_transition_ifm,
                "fragments_crs": fragments_crs,
                "ifm_source_col": ifm_source_col,
                "ifm_threshold": ifm_threshold,
                "ifm_target_managed_share": ifm_target_managed_share,
                "seral_stage_config_path": seral_stage_config_path,
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
        cc_transition_ifm="managed",
        fragments_crs="EPSG:3005",
        ifm_source_col="thlb_raw",
        ifm_threshold=0.2,
        ifm_target_managed_share=None,
        seral_stage_config=Path("config/seral.k3z.yaml"),
    )

    assert called["tsa_list"] == ["k3z"]
    assert called["cc_max_age"] == 500
    assert called["cc_transition_ifm"] == "managed"
    assert called["ifm_source_col"] == "thlb_raw"
    assert called["ifm_threshold"] == pytest.approx(0.2)
    assert (
        Path(called["seral_stage_config_path"])
        .as_posix()
        .endswith("config/seral.k3z.yaml")
    )
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
                "cc_min_age": cc_min_age,
                "cc_max_age": cc_max_age,
                "fragments_crs": fragments_crs,
            }
        )
        return SimpleNamespace(
            yields_csv_path=Path("output/woodstock/woodstock_yields.csv"),
            areas_csv_path=Path("output/woodstock/woodstock_areas.csv"),
            actions_csv_path=Path("output/woodstock/woodstock_actions.csv"),
            transitions_csv_path=Path("output/woodstock/woodstock_transitions.csv"),
            tsa_list=tsa_list,
            yield_rows=1234,
            area_rows=567,
            action_rows=12,
            transition_rows=12,
        )

    monkeypatch.setattr(
        cli_main, "export_woodstock_package", _fake_export_woodstock_package
    )

    cli_main.export_woodstock(
        tsa=["k3z"],
        bundle_dir=Path("data/model_input_bundle"),
        checkpoint=Path("data/ria_vri_vclr1p_checkpoint7.feather"),
        output_dir=Path("output/woodstock"),
        cc_min_age=0,
        cc_max_age=500,
        fragments_crs="EPSG:3005",
    )

    assert called["tsa_list"] == ["k3z"]
    assert called["cc_max_age"] == 500
    assert called["fragments_crs"] == "EPSG:3005"
    assert any("woodstock export completed" in msg for msg in messages)


def test_export_release_calls_packager(monkeypatch: pytest.MonkeyPatch) -> None:
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)
    called: dict[str, object] = {}

    def _fake_build_release_package(
        *,
        case_id,
        output_root,
        model_input_bundle_dir,
        patchworks_output_dir,
        woodstock_output_dir,
        logs_dir,
        run_id,
        strict,
    ):
        called.update(
            {
                "case_id": case_id,
                "output_root": output_root,
                "model_input_bundle_dir": model_input_bundle_dir,
                "patchworks_output_dir": patchworks_output_dir,
                "woodstock_output_dir": woodstock_output_dir,
                "logs_dir": logs_dir,
                "run_id": run_id,
                "strict": strict,
            }
        )
        return SimpleNamespace(
            release_id="k3z_test",
            release_dir=Path("releases/k3z_test"),
            manifest_path=Path("releases/k3z_test/release_manifest.json"),
            handoff_notes_path=Path("releases/k3z_test/HANDOFF.md"),
        )

    monkeypatch.setattr(cli_main, "build_release_package", _fake_build_release_package)

    cli_main.export_release(
        case_id="k3z",
        output_root=Path("releases"),
        bundle_dir=Path("data/model_input_bundle"),
        patchworks_dir=Path("output/patchworks_k3z_validated"),
        woodstock_dir=Path("output/woodstock_k3z_validated"),
        logs_dir=Path("vdyp_io/logs"),
        run_id="test",
        strict=True,
    )

    assert called["case_id"] == "k3z"
    assert called["strict"] is True
    assert any("release package built" in msg for msg in messages)


def test_patchworks_preflight_reports_config_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)

    def _fail_load(_path: Path) -> None:
        raise FileNotFoundError("missing config")

    monkeypatch.setattr(cli_main, "load_patchworks_runtime_config", _fail_load)

    with pytest.raises(typer.Exit) as exc_info:
        cli_main.patchworks_preflight(config=Path("missing.yaml"))

    assert exc_info.value.exit_code == 1
    assert any("Patchworks config error" in msg for msg in messages)


def test_patchworks_preflight_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)
    runtime_cfg = SimpleNamespace(
        jar_path=Path("reference/Patchworks/patchworks.jar"),
        license_env="SPS_LICENSE_SERVER",
        license_value="frst424@auth.spatial.ca",
        spshome="Z:\\Patchworks",
    )
    monkeypatch.setattr(
        cli_main, "load_patchworks_runtime_config", lambda _path: runtime_cfg
    )
    monkeypatch.setattr(
        cli_main,
        "run_patchworks_preflight",
        lambda **_kwargs: SimpleNamespace(
            warnings=(),
            errors=(),
            launcher_executable="/usr/bin/wine64",
            host_mode="wine",
            license_host="auth.spatial.ca",
        ),
    )

    cli_main.patchworks_preflight(config=Path("config/patchworks.runtime.yaml"))

    assert any("Patchworks preflight passed" in msg for msg in messages)
    assert any("license_host=auth.spatial.ca" in msg for msg in messages)


def test_patchworks_matrix_build_emits_logs(monkeypatch: pytest.MonkeyPatch) -> None:
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)
    runtime_cfg = SimpleNamespace()
    monkeypatch.setattr(
        cli_main, "load_patchworks_runtime_config", lambda _path: runtime_cfg
    )
    monkeypatch.setattr(
        cli_main,
        "run_patchworks_command",
        lambda **_kwargs: SimpleNamespace(
            run_id="pwtest",
            returncode=0,
            command=("wine64", "cmd", "/c", "java -jar patchworks.jar"),
            stdout_log_path=Path(
                "vdyp_io/logs/patchworks_matrixbuilder_stdout-pwtest.log"
            ),
            stderr_log_path=Path(
                "vdyp_io/logs/patchworks_matrixbuilder_stderr-pwtest.log"
            ),
            manifest_path=Path(
                "vdyp_io/logs/patchworks_matrixbuilder_manifest-pwtest.json"
            ),
            failures=(),
        ),
    )

    cli_main.patchworks_matrix_build(
        config=Path("config/patchworks.runtime.yaml"),
        log_dir=Path("vdyp_io/logs"),
        run_id="pwtest",
        interactive=False,
    )

    assert any("Patchworks matrix-builder run complete" in msg for msg in messages)
    assert any("stdout_log:" in msg for msg in messages)


def test_patchworks_build_blocks_emits_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)
    runtime_cfg = SimpleNamespace()
    monkeypatch.setattr(
        cli_main, "load_patchworks_runtime_config", lambda _path: runtime_cfg
    )
    monkeypatch.setattr(
        cli_main,
        "build_patchworks_blocks_dataset",
        lambda **_kwargs: SimpleNamespace(
            model_dir=Path("C:/model"),
            blocks_shapefile_path=Path("C:/model/blocks/blocks.shp"),
            topology_csv_path=Path("C:/model/blocks/topology_blocks_200r.csv"),
            block_count=218,
            stand_id_field="FEATURE_ID",
            topology_edge_count=1024,
            topology_radius_m=200.0,
        ),
    )

    cli_main.patchworks_build_blocks(
        config=Path("config/patchworks.runtime.yaml"),
        model_dir=None,
        fragments_shp=None,
        topology_radius=200.0,
        with_topology=True,
    )

    assert any("Patchworks blocks build complete" in msg for msg in messages)
    assert any("blocks_shapefile:" in msg for msg in messages)
    assert any("topology_csv:" in msg for msg in messages)


def test_patchworks_build_blocks_reports_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)

    def _fail_load(_path: Path) -> None:
        raise FileNotFoundError("missing config")

    monkeypatch.setattr(cli_main, "load_patchworks_runtime_config", _fail_load)

    with pytest.raises(typer.Exit) as exc_info:
        cli_main.patchworks_build_blocks(
            config=Path("missing.yaml"),
            model_dir=None,
            fragments_shp=None,
            topology_radius=200.0,
            with_topology=True,
        )

    assert exc_info.value.exit_code == 1
    assert any("Patchworks block build failed" in msg for msg in messages)


def test_instance_init_calls_bootstrap(monkeypatch: pytest.MonkeyPatch) -> None:
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)
    called: dict[str, object] = {}

    def _fake_bootstrap_instance_workspace(
        *,
        instance_root,
        overwrite,
        include_bc_vri_download,
        message_fn,
    ):
        called["instance_root"] = instance_root
        called["overwrite"] = overwrite
        called["include_bc_vri_download"] = include_bc_vri_download
        message_fn("download simulation")
        return SimpleNamespace(
            instance_root=instance_root,
            created_dirs=(),
            written_files=(instance_root / "QUICKSTART.md",),
            skipped_files=(),
            downloaded_archives=(),
            extracted_dirs=(),
        )

    monkeypatch.setattr(
        cli_main,
        "bootstrap_instance_workspace",
        _fake_bootstrap_instance_workspace,
    )

    cli_main.instance_init(
        instance_root=Path("instance"),
        overwrite=True,
        download_bc_vri=False,
        yes=True,
    )

    assert called["instance_root"].name == "instance"
    assert called["overwrite"] is True
    assert called["include_bc_vri_download"] is False
    assert any("instance init completed" in msg for msg in messages)

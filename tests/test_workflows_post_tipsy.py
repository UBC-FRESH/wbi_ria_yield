from __future__ import annotations

import json
import os
from pathlib import Path
import pickle

import pandas as pd

from femic.workflows.legacy import (
    PostTipsyBundleResult,
    run_post_tipsy_bundle,
    run_post_tipsy_bundle_with_manifest,
)


def test_run_post_tipsy_bundle_builds_bundle_from_cached_artifacts(
    tmp_path: Path,
) -> None:
    data_root = tmp_path / "data"
    data_root.mkdir(parents=True, exist_ok=True)
    tsa = "29"

    results_for_tsa = [
        (0, "IDF_FD", {"L": {"ss": None}, "M": {"ss": None}, "H": {"ss": None}})
    ]
    with (data_root / f"vdyp_prep-tsa{tsa}.pkl").open("wb") as fh:
        pickle.dump(results_for_tsa, fh)

    vdyp_curves = pd.DataFrame(
        {
            "stratum_code": [
                "IDF_FD",
                "IDF_FD",
                "IDF_FD",
                "IDF_FD",
                "IDF_FD",
                "IDF_FD",
            ],
            "si_level": ["L", "L", "M", "M", "H", "H"],
            "age": [0, 10, 0, 10, 0, 10],
            "volume": [0.0, 10.0, 0.0, 20.0, 0.0, 30.0],
        }
    )
    vdyp_curves.to_feather(data_root / f"vdyp_curves_smooth-tsa{tsa}.feather")

    pd.DataFrame({"AU": [21000]}).to_excel(
        data_root / f"tipsy_params_tsa{tsa}.xlsx",
        index=False,
        sheet_name="TIPSY_inputTBL",
    )
    (data_root / f"04_output-tsa{tsa}.out").write_text(
        "placeholder\n", encoding="utf-8"
    )

    def _fake_run_01b(
        *,
        tsa: str,
        results,
        au_scsi,
        tipsy_curves,
        vdyp_curves_smooth,
        runtime_config,
    ) -> None:
        _ = (results, au_scsi, vdyp_curves_smooth, runtime_config)
        tipsy_df = pd.DataFrame(
            {
                "AU": [21000, 21000, 22000, 22000, 23000, 23000],
                "Age": [0, 10, 0, 10, 0, 10],
                "Yield": [0.0, 12.0, 0.0, 24.0, 0.0, 36.0],
                "Height": [0.0, 2.0, 0.0, 3.0, 0.0, 4.0],
                "DBHq": [0.0, 1.0, 0.0, 1.5, 0.0, 2.0],
                "TPH": [1000, 900, 1000, 900, 1000, 900],
            }
        ).set_index(["AU", "Age"])
        tipsy_curves[tsa] = tipsy_df
        tipsy_df.reset_index().to_csv(
            data_root / f"tipsy_curves_tsa{tsa}.csv",
            index=False,
        )
        pd.DataFrame({"AU": [21000], "FD": [100.0]}).to_csv(
            data_root / f"tipsy_sppcomp_tsa{tsa}.csv",
            index=False,
        )

    result = run_post_tipsy_bundle(
        tsa_list=[tsa],
        repo_root=tmp_path,
        data_root=data_root,
        run_01b_fn=_fake_run_01b,
        message_fn=lambda _msg: None,
    )

    assert result.tsa_list == [tsa]
    assert result.au_rows == 3
    assert result.curve_rows == 6
    assert result.curve_points_rows == 12
    assert result.au_table_path.is_file()
    assert result.curve_table_path.is_file()
    assert result.curve_points_table_path.is_file()


def test_run_post_tipsy_bundle_sets_managed_curve_env_for_01b(
    tmp_path: Path,
    monkeypatch,
) -> None:
    data_root = tmp_path / "data"
    data_root.mkdir(parents=True, exist_ok=True)
    tsa = "29"

    results_for_tsa = [
        (0, "IDF_FD", {"L": {"ss": None}, "M": {"ss": None}, "H": {"ss": None}})
    ]
    with (data_root / f"vdyp_prep-tsa{tsa}.pkl").open("wb") as fh:
        pickle.dump(results_for_tsa, fh)
    pd.DataFrame(
        {
            "stratum_code": ["IDF_FD", "IDF_FD"],
            "si_level": ["L", "L"],
            "age": [0, 10],
            "volume": [0.0, 10.0],
        }
    ).to_feather(data_root / f"vdyp_curves_smooth-tsa{tsa}.feather")
    pd.DataFrame({"AU": [21000]}).to_excel(
        data_root / f"tipsy_params_tsa{tsa}.xlsx",
        index=False,
        sheet_name="TIPSY_inputTBL",
    )
    (data_root / f"04_output-tsa{tsa}.out").write_text(
        "placeholder\n", encoding="utf-8"
    )

    seen_env: dict[str, str | None] = {}

    def _fake_run_01b(
        *,
        tsa: str,
        results,
        au_scsi,
        tipsy_curves,
        vdyp_curves_smooth,
        runtime_config,
    ) -> None:
        _ = (results, au_scsi, vdyp_curves_smooth, runtime_config)
        seen_env["mode"] = os.environ.get("FEMIC_MANAGED_CURVE_MODE")
        seen_env["x"] = os.environ.get("FEMIC_MANAGED_CURVE_X_SCALE")
        seen_env["y"] = os.environ.get("FEMIC_MANAGED_CURVE_Y_SCALE")
        seen_env["truncate"] = os.environ.get("FEMIC_MANAGED_CURVE_TRUNCATE_AT_CULM")
        seen_env["max_age"] = os.environ.get("FEMIC_MANAGED_CURVE_MAX_AGE")
        tipsy_df = pd.DataFrame(
            {
                "AU": [21000, 21000, 22000, 22000, 23000, 23000],
                "Age": [0, 10, 0, 10, 0, 10],
                "Yield": [0.0, 12.0, 0.0, 24.0, 0.0, 36.0],
                "Height": [0.0, 2.0, 0.0, 3.0, 0.0, 4.0],
                "DBHq": [0.0, 1.0, 0.0, 1.5, 0.0, 2.0],
                "TPH": [1000, 900, 1000, 900, 1000, 900],
            }
        ).set_index(["AU", "Age"])
        tipsy_curves[tsa] = tipsy_df
        tipsy_df.reset_index().to_csv(
            data_root / f"tipsy_curves_tsa{tsa}.csv",
            index=False,
        )
        pd.DataFrame({"AU": [21000], "FD": [100.0]}).to_csv(
            data_root / f"tipsy_sppcomp_tsa{tsa}.csv",
            index=False,
        )

    monkeypatch.delenv("FEMIC_MANAGED_CURVE_MODE", raising=False)
    monkeypatch.delenv("FEMIC_MANAGED_CURVE_X_SCALE", raising=False)
    monkeypatch.delenv("FEMIC_MANAGED_CURVE_Y_SCALE", raising=False)
    monkeypatch.delenv("FEMIC_MANAGED_CURVE_TRUNCATE_AT_CULM", raising=False)
    monkeypatch.delenv("FEMIC_MANAGED_CURVE_MAX_AGE", raising=False)

    run_post_tipsy_bundle(
        tsa_list=[tsa],
        repo_root=tmp_path,
        data_root=data_root,
        run_01b_fn=_fake_run_01b,
        managed_curve_mode="vdyp_transform",
        managed_curve_x_scale=0.8,
        managed_curve_y_scale=1.2,
        managed_curve_truncate_at_culm=True,
        managed_curve_max_age=300,
        message_fn=lambda _msg: None,
    )

    assert seen_env["mode"] == "vdyp_transform"
    assert seen_env["x"] == "0.8"
    assert seen_env["y"] == "1.2"
    assert seen_env["truncate"] == "1"
    assert seen_env["max_age"] == "300"
    assert os.environ.get("FEMIC_MANAGED_CURVE_MODE") is None


def test_run_post_tipsy_bundle_with_manifest_writes_manifest(
    tmp_path: Path,
) -> None:
    log_dir = tmp_path / "logs"
    expected_result = PostTipsyBundleResult(
        tsa_list=["29"],
        au_rows=30,
        curve_rows=60,
        curve_points_rows=1234,
        tipsy_curves_paths=[tmp_path / "data" / "tipsy_curves_tsa29.csv"],
        tipsy_sppcomp_paths=[tmp_path / "data" / "tipsy_sppcomp_tsa29.csv"],
        au_table_path=tmp_path / "data" / "model_input_bundle" / "au_table.csv",
        curve_table_path=tmp_path / "data" / "model_input_bundle" / "curve_table.csv",
        curve_points_table_path=tmp_path
        / "data"
        / "model_input_bundle"
        / "curve_points_table.csv",
    )
    for path in [
        *expected_result.tipsy_curves_paths,
        *expected_result.tipsy_sppcomp_paths,
        expected_result.au_table_path,
        expected_result.curve_table_path,
        expected_result.curve_points_table_path,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n", encoding="utf-8")

    def _fake_run_post_tipsy_bundle(**_kwargs):
        return expected_result

    # Patch at module import boundary to avoid preparing real TSA artifacts here.
    import femic.workflows.legacy as legacy_module

    original = legacy_module.run_post_tipsy_bundle
    legacy_module.run_post_tipsy_bundle = _fake_run_post_tipsy_bundle
    try:
        run_result = run_post_tipsy_bundle_with_manifest(
            tsa_list=["29"],
            run_id="post_tipsy_manifest_test",
            log_dir=log_dir,
            message_fn=lambda _msg: None,
        )
    finally:
        legacy_module.run_post_tipsy_bundle = original

    assert run_result.result == expected_result
    assert run_result.manifest_path.is_file()
    payload = json.loads(run_result.manifest_path.read_text(encoding="utf-8"))
    assert payload["status"] == "ok"
    assert payload["workflow"] == "tsa_post_tipsy"
    assert payload["run_id"] == "post_tipsy_manifest_test"

from __future__ import annotations

from pathlib import Path
import pickle

import pandas as pd

from femic.workflows.legacy import run_post_tipsy_bundle


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

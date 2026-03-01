from __future__ import annotations

from pathlib import Path

from femic.pipeline.pre_vdyp import (
    load_vdyp_prep_checkpoint,
    save_vdyp_prep_checkpoint,
    serialize_vdyp_prep_payload,
)


def test_serialize_vdyp_prep_payload_removes_fit_func() -> None:
    fit_func = lambda x: x  # noqa: E731
    results = [
        [
            0,
            "BWBS_SW",
            {
                "L": {
                    "species": {
                        "SW": {
                            "pct": 70,
                            "fit_func": fit_func,
                        }
                    }
                }
            },
        ]
    ]

    payload = serialize_vdyp_prep_payload(results)

    assert payload[0][2]["L"]["species"]["SW"]["pct"] == 70
    assert "fit_func" not in payload[0][2]["L"]["species"]["SW"]
    assert "fit_func" in results[0][2]["L"]["species"]["SW"]


def test_save_and_load_vdyp_prep_checkpoint_roundtrip(tmp_path: Path) -> None:
    checkpoint = tmp_path / "vdyp_prep.pkl"
    results = [[1, "BWBS_PL", {"M": {"species": {"PL": {"pct": 55}}}}]]

    count = save_vdyp_prep_checkpoint(checkpoint, results)
    loaded = load_vdyp_prep_checkpoint(checkpoint)

    assert count == 1
    assert loaded == [[1, "BWBS_PL", {"M": {"species": {"PL": {"pct": 55}}}}]]

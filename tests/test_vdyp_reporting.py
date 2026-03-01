from __future__ import annotations

from pathlib import Path

from femic.vdyp.reporting import summarize_vdyp_logs


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def test_summarize_vdyp_logs_counts_and_anchor_match(tmp_path: Path) -> None:
    curve_log = tmp_path / "curve.jsonl"
    run_log = tmp_path / "run.jsonl"
    _write(
        curve_log,
        "\n".join(
            [
                '{"status":"ok","stage":"toe_fit","first_age":1.0,"first_volume":1e-6,'
                '"context":{"tsa":"08"}}',
                '{"status":"warning","stage":"curve_input","context":{"tsa":"08"}}',
                "not-json",
            ]
        )
        + "\n",
    )
    _write(
        run_log,
        "\n".join(
            [
                '{"status":"dispatch","phase":"bootstrap","context":{"tsa":"08"}}',
                '{"status":"ok","phase":"auto_small_sample","context":{"tsa":"08"}}',
                "[]",
            ]
        )
        + "\n",
    )

    summary = summarize_vdyp_logs(
        curve_log_path=curve_log,
        run_log_path=run_log,
        expected_first_age=1.0,
        expected_first_volume=1e-6,
        tolerance=1e-12,
    )

    assert summary.curve_events == 2
    assert summary.curve_parse_errors == 1
    assert summary.curve_status_counts == {"ok": 1, "warning": 1}
    assert summary.curve_stage_counts == {"curve_input": 1, "toe_fit": 1}
    assert summary.first_point_events == 1
    assert summary.first_point_matches == 1
    assert summary.first_point_mismatches == 0

    assert summary.run_events == 2
    assert summary.run_parse_errors == 1
    assert summary.run_status_counts == {"dispatch": 1, "ok": 1}
    assert summary.run_phase_counts == {"auto_small_sample": 1, "bootstrap": 1}

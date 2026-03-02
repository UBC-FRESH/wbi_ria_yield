from __future__ import annotations

from femic.pipeline.diagnostics import (
    build_contextual_error_message,
    build_timestamped_event,
    format_context_kv,
)


def test_format_context_kv_skips_none_by_default() -> None:
    out = format_context_kv(context={"tsa": "08", "reason": None, "mode": "auto"})
    assert out == "tsa=08, mode=auto"


def test_build_contextual_error_message_includes_prefix_and_context() -> None:
    out = build_contextual_error_message(
        prefix="bad rule",
        context={"tsa": "41", "forest_type": 2},
    )
    assert out == "bad rule: tsa=41, forest_type=2"


def test_build_contextual_error_message_returns_prefix_when_no_context() -> None:
    out = build_contextual_error_message(prefix="error", context={"a": None})
    assert out == "error"


def test_build_timestamped_event_allows_omitting_status() -> None:
    out = build_timestamped_event(
        event="vdyp_curve",
        timestamp="2026-01-01T00:00:00+00:00",
        context={"tsa": "08"},
    )
    assert out["event"] == "vdyp_curve"
    assert out["timestamp"] == "2026-01-01T00:00:00+00:00"
    assert out["context"] == {"tsa": "08"}
    assert "status" not in out

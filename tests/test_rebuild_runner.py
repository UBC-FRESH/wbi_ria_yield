from __future__ import annotations

from datetime import UTC, datetime, timedelta
import json
from pathlib import Path

import pytest

from femic.rebuild_runner import (
    JsonRebuildReportSink,
    RebuildRunner,
    RebuildStep,
)


def _tick_clock(start: datetime) -> tuple[callable[[], datetime], list[datetime]]:
    points = [start + timedelta(seconds=i) for i in range(30)]
    state = {"idx": 0}

    def _now() -> datetime:
        value = points[state["idx"]]
        state["idx"] += 1
        return value

    return _now, points


def test_rebuild_runner_executes_in_deterministic_topological_order() -> None:
    executed: list[str] = []
    now_fn, _ = _tick_clock(datetime(2026, 3, 11, 10, 0, tzinfo=UTC))

    def _mk(step_id: str):
        def _action(_ctx: dict[str, object]) -> dict[str, object]:
            executed.append(step_id)
            return {"last_step": step_id}

        return _action

    steps = [
        RebuildStep(step_id="a", action=_mk("a")),
        RebuildStep(step_id="b", action=_mk("b")),
        RebuildStep(step_id="c", action=_mk("c"), depends_on=("a", "b")),
    ]

    report = RebuildRunner(steps=steps, now_fn=now_fn).run(run_id="run1")

    assert report.failed is False
    assert report.planned_order == ("a", "b", "c")
    assert executed == ["a", "b", "c"]
    assert [outcome.status for outcome in report.outcomes] == ["ok", "ok", "ok"]


def test_rebuild_runner_stops_on_failure_by_default() -> None:
    executed: list[str] = []
    now_fn, _ = _tick_clock(datetime(2026, 3, 11, 11, 0, tzinfo=UTC))

    def _ok(_ctx: dict[str, object]) -> dict[str, object]:
        executed.append("ok")
        return {}

    def _boom(_ctx: dict[str, object]) -> dict[str, object]:
        executed.append("boom")
        raise RuntimeError("step failed")

    def _after(_ctx: dict[str, object]) -> dict[str, object]:
        executed.append("after")
        return {}

    steps = [
        RebuildStep(step_id="ok", action=_ok),
        RebuildStep(step_id="boom", action=_boom, depends_on=("ok",)),
        RebuildStep(step_id="after", action=_after, depends_on=("boom",)),
    ]
    report = RebuildRunner(steps=steps, now_fn=now_fn).run(run_id="run2")

    assert report.failed is True
    assert executed == ["ok", "boom"]
    assert len(report.outcomes) == 2
    assert report.outcomes[-1].status == "failed"
    assert "RuntimeError" in (report.outcomes[-1].error or "")


def test_rebuild_runner_can_continue_after_failure() -> None:
    executed: list[str] = []
    now_fn, _ = _tick_clock(datetime(2026, 3, 11, 12, 0, tzinfo=UTC))

    def _boom(_ctx: dict[str, object]) -> dict[str, object]:
        executed.append("boom")
        raise ValueError("bad")

    def _next(_ctx: dict[str, object]) -> dict[str, object]:
        executed.append("next")
        return {}

    steps = [
        RebuildStep(step_id="boom", action=_boom),
        RebuildStep(step_id="next", action=_next),
    ]
    report = RebuildRunner(
        steps=steps,
        now_fn=now_fn,
        stop_on_failure=False,
    ).run(run_id="run3")

    assert report.failed is True
    assert executed == ["boom", "next"]
    assert len(report.outcomes) == 2


def test_rebuild_runner_writes_json_report(tmp_path: Path) -> None:
    now_fn, _ = _tick_clock(datetime(2026, 3, 11, 13, 0, tzinfo=UTC))
    sink_path = tmp_path / "logs" / "rebuild-report.json"
    sink = JsonRebuildReportSink(path=sink_path)

    steps = [RebuildStep(step_id="only", action=lambda _ctx: {"x": 1})]
    report = RebuildRunner(steps=steps, now_fn=now_fn, report_sink=sink).run(
        run_id="run4"
    )

    assert sink_path.exists()
    payload = json.loads(sink_path.read_text(encoding="utf-8"))
    assert payload["run_id"] == "run4"
    assert payload["planned_order"] == ["only"]
    assert payload["outcomes"][0]["status"] == "ok"
    assert report.outcomes[0].metadata["x"] == 1


def test_rebuild_runner_rejects_unknown_dependency() -> None:
    steps = [RebuildStep(step_id="a", action=lambda _ctx: {}, depends_on=("missing",))]
    runner = RebuildRunner(steps=steps)
    with pytest.raises(ValueError, match="unknown step"):
        runner.run(run_id="run5")


def test_rebuild_runner_rejects_cyclic_dependencies() -> None:
    steps = [
        RebuildStep(step_id="a", action=lambda _ctx: {}, depends_on=("b",)),
        RebuildStep(step_id="b", action=lambda _ctx: {}, depends_on=("a",)),
    ]
    runner = RebuildRunner(steps=steps)
    with pytest.raises(ValueError, match="cycle"):
        runner.run(run_id="run6")

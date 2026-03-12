"""Reusable deterministic rebuild runner with JSON report sink support."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol


StepAction = Callable[[dict[str, Any]], Mapping[str, Any] | None]


@dataclass(frozen=True)
class RebuildStep:
    """One step in a rebuild graph."""

    step_id: str
    action: StepAction
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True)
class StepOutcome:
    """Execution result for one rebuild step."""

    step_id: str
    status: str
    started_at_utc: str
    finished_at_utc: str
    duration_seconds: float
    metadata: dict[str, Any]
    error: str | None


@dataclass(frozen=True)
class RebuildExecutionReport:
    """Run-level report for a rebuild execution."""

    run_id: str
    started_at_utc: str
    finished_at_utc: str
    failed: bool
    planned_order: tuple[str, ...]
    outcomes: tuple[StepOutcome, ...]


class RebuildReportSink(Protocol):
    """Report sink protocol for rebuild execution artifacts."""

    def write(self, report: RebuildExecutionReport) -> None:
        """Persist a rebuild report."""


class JsonRebuildReportSink:
    """Write rebuild execution reports to JSON files."""

    def __init__(self, *, path: Path):
        self.path = path

    def write(self, report: RebuildExecutionReport) -> None:
        """Serialize a rebuild execution report to the configured JSON path."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")


class RebuildRunner:
    """Execute rebuild steps in deterministic topological order."""

    def __init__(
        self,
        *,
        steps: list[RebuildStep],
        report_sink: RebuildReportSink | None = None,
        now_fn: Callable[[], datetime] | None = None,
        stop_on_failure: bool = True,
    ) -> None:
        self._steps = steps
        self._report_sink = report_sink
        self._now_fn = now_fn or (lambda: datetime.now(UTC))
        self._stop_on_failure = stop_on_failure

    def _resolve_order(self) -> list[RebuildStep]:
        id_to_step = {step.step_id: step for step in self._steps}
        if len(id_to_step) != len(self._steps):
            raise ValueError("Duplicate step_id values are not allowed.")

        indegree: dict[str, int] = {step.step_id: 0 for step in self._steps}
        dependents: dict[str, list[str]] = defaultdict(list)
        index = {step.step_id: idx for idx, step in enumerate(self._steps)}

        for step in self._steps:
            for dep in step.depends_on:
                if dep not in id_to_step:
                    raise ValueError(
                        f"Step {step.step_id!r} depends on unknown step {dep!r}."
                    )
                indegree[step.step_id] += 1
                dependents[dep].append(step.step_id)

        ready = deque(
            step.step_id
            for step in sorted(self._steps, key=lambda item: index[item.step_id])
            if indegree[step.step_id] == 0
        )
        ordered_ids: list[str] = []

        while ready:
            current = ready.popleft()
            ordered_ids.append(current)
            for child in sorted(
                dependents.get(current, []), key=lambda value: index[value]
            ):
                indegree[child] -= 1
                if indegree[child] == 0:
                    ready.append(child)

        if len(ordered_ids) != len(self._steps):
            raise ValueError("Rebuild step graph contains a cycle.")
        return [id_to_step[step_id] for step_id in ordered_ids]

    def run(
        self,
        *,
        run_id: str,
        context: dict[str, Any] | None = None,
    ) -> RebuildExecutionReport:
        """Execute configured steps, persist report if configured, and return it."""
        ordered_steps = self._resolve_order()
        started_at = self._now_fn()
        runtime_context = dict(context or {})
        outcomes: list[StepOutcome] = []
        failed = False

        for step in ordered_steps:
            step_started = self._now_fn()
            status = "ok"
            metadata: dict[str, Any] = {}
            error_text: str | None = None
            try:
                result = step.action(runtime_context)
                if result is not None:
                    metadata = dict(result)
                    runtime_context.update(metadata)
            except (
                Exception
            ) as exc:  # pragma: no cover - exact failures are caller-defined
                failed = True
                status = "failed"
                error_text = f"{type(exc).__name__}: {exc}"
            step_finished = self._now_fn()
            outcomes.append(
                StepOutcome(
                    step_id=step.step_id,
                    status=status,
                    started_at_utc=_iso_utc(step_started),
                    finished_at_utc=_iso_utc(step_finished),
                    duration_seconds=(step_finished - step_started).total_seconds(),
                    metadata=metadata,
                    error=error_text,
                )
            )
            if failed and self._stop_on_failure:
                break

        finished_at = self._now_fn()
        report = RebuildExecutionReport(
            run_id=run_id,
            started_at_utc=_iso_utc(started_at),
            finished_at_utc=_iso_utc(finished_at),
            failed=failed,
            planned_order=tuple(step.step_id for step in ordered_steps),
            outcomes=tuple(outcomes),
        )
        if self._report_sink is not None:
            self._report_sink.write(report)
        return report


def _iso_utc(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return (
        value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )

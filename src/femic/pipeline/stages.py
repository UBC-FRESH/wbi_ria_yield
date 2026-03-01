"""Pipeline stage executors used by workflow wrappers."""

from __future__ import annotations

from dataclasses import dataclass
import subprocess
import sys

from femic.pipeline.io import LegacyExecutionPlan


@dataclass(frozen=True)
class StageResult:
    """Result returned by a stage executor."""

    exit_code: int


def run_legacy_subprocess(
    *,
    execution_plan: LegacyExecutionPlan,
    drop_lines: set[str],
) -> StageResult:
    """Execute legacy script and stream output while filtering known noisy lines."""
    process = subprocess.Popen(
        execution_plan.cmd,
        cwd=str(execution_plan.script_path.parent),
        env=execution_plan.env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert process.stdout is not None
    for line in process.stdout:
        if line.strip() in drop_lines:
            continue
        sys.stdout.write(line)
    return StageResult(exit_code=process.wait())

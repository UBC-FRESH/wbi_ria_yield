"""Pipeline stage executors used by workflow wrappers."""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any, Callable, Sequence

from femic.pipeline.io import LegacyExecutionPlan


@dataclass(frozen=True)
class StageResult:
    """Result returned by a stage executor."""

    exit_code: int


def load_legacy_module(
    *,
    script_path: str | Path,
    module_name: str,
) -> ModuleType:
    """Load a Python module from a legacy script path."""
    resolved_path = Path(script_path)
    spec = importlib.util.spec_from_file_location(module_name, resolved_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module spec for {resolved_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_legacy_tsa_loop(
    *,
    tsa_list: Sequence[str],
    should_skip_fn: Callable[[str], bool],
    run_one_fn: Callable[[str], Any],
) -> None:
    """Run one legacy stage per TSA with caller-provided skip logic."""
    for tsa in tsa_list:
        if should_skip_fn(tsa):
            continue
        run_one_fn(tsa)


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

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


@dataclass
class LegacyTSAStageState:
    """Mutable state maps shared across legacy TSA stages."""

    vdyp_curves_smooth: dict[str, Any]
    vdyp_results: dict[str, Any]
    tipsy_params: dict[str, Any]
    tipsy_curves: dict[str, Any]
    scsi_au: dict[str, Any]
    au_scsi: dict[str, Any]
    results: dict[str, Any]


def initialize_legacy_tsa_stage_state() -> LegacyTSAStageState:
    """Create empty state payload used by legacy 01a/01b TSA stages."""
    return LegacyTSAStageState(
        vdyp_curves_smooth={},
        vdyp_results={},
        tipsy_params={},
        tipsy_curves={},
        scsi_au={},
        au_scsi={},
        results={},
    )


def prepare_tsa_index(
    *,
    f_table: Any,
    tsa_column: str = "tsa_code",
) -> Any:
    """Ensure legacy table uses TSA code as index for downstream stage lookups."""
    if getattr(f_table, "index", None) is not None and f_table.index.name == tsa_column:
        return f_table
    return f_table.set_index(tsa_column)


def should_skip_if_outputs_exist(
    *,
    resume_effective: bool,
    output_paths: Sequence[str | Path],
    skip_message: str,
    print_fn: Callable[[str], Any] = print,
) -> bool:
    """Return True when resume mode is on and all required outputs already exist."""
    if not resume_effective:
        return False
    if not all(Path(path).is_file() for path in output_paths):
        return False
    print_fn(skip_message)
    return True


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

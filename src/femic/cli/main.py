"""Typer-based CLI entry point for FEMIC."""

from __future__ import annotations

from pathlib import Path
import shutil

import typer
from rich.console import Console

from femic import __version__
from femic.vdyp.reporting import (
    VdypWarningBudget,
    evaluate_warning_budget,
    summarize_vdyp_logs,
)
from femic.workflows.legacy import run_data_prep

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Forest Estate Model Input Compiler (FEMIC).",
)
prep_app = typer.Typer(
    add_completion=False, no_args_is_help=True, help="Prepare data inputs."
)
vdyp_app = typer.Typer(
    add_completion=False, no_args_is_help=True, help="Run VDYP workflows."
)
tsa_app = typer.Typer(
    add_completion=False, no_args_is_help=True, help="Process individual TSAs."
)
console = Console()

DATA_ROOT_OPTION = typer.Option(
    Path("data"),
    "--data-root",
    help="Root directory for input data.",
)
OUTPUT_ROOT_OPTION = typer.Option(
    Path("outputs"),
    "--output-root",
    help="Root directory for generated outputs.",
)
TSA_OPTION = typer.Option(
    None,
    "--tsa",
    help="Limit processing to TSA code(s). Can be provided multiple times.",
    show_default=False,
)
RESUME_OPTION = typer.Option(
    False,
    "--resume",
    help="Skip steps that appear to be completed already.",
)
DRY_RUN_OPTION = typer.Option(
    False,
    "--dry-run",
    help="Show planned work without executing.",
)
VERBOSE_OPTION = typer.Option(
    False,
    "--verbose",
    "-v",
    help="Enable verbose output.",
)
VERSION_OPTION = typer.Option(
    False,
    "--version",
    help="Show version and exit.",
)
DEBUG_OPTION = typer.Option(
    False,
    "--debug",
    help="Enable rich tracebacks.",
)
SKIP_CHECKS_OPTION = typer.Option(
    False,
    "--skip-checks",
    help="Skip preflight checks for external tools and inputs.",
)
DEBUG_ROWS_OPTION = typer.Option(
    None,
    "--debug-rows",
    help="Limit pipeline input rows for faster debugging (uses head(N)).",
    show_default=False,
)
RUN_ID_OPTION = typer.Option(
    None,
    "--run-id",
    help="Optional run identifier for manifest/log file naming.",
    show_default=False,
)
LOG_DIR_OPTION = typer.Option(
    Path("vdyp_io/logs"),
    "--log-dir",
    help="Directory for run manifests and run-scoped VDYP JSONL logs.",
)
VDYP_CURVE_LOG_OPTION = typer.Option(
    Path("vdyp_io/logs/vdyp_curve_events.jsonl"),
    "--curve-log",
    help="Path to VDYP curve-event JSONL log.",
)
VDYP_RUN_LOG_OPTION = typer.Option(
    Path("vdyp_io/logs/vdyp_runs.jsonl"),
    "--run-log",
    help="Path to VDYP run-event JSONL log.",
)
VDYP_EXPECTED_FIRST_AGE_OPTION = typer.Option(
    1.0,
    "--expected-first-age",
    help="Expected first age point used for curve anchoring checks.",
)
VDYP_EXPECTED_FIRST_VOLUME_OPTION = typer.Option(
    1e-6,
    "--expected-first-volume",
    help="Expected first volume point used for curve anchoring checks.",
)
VDYP_TOLERANCE_OPTION = typer.Option(
    1e-12,
    "--tolerance",
    help="Absolute tolerance for first-point anchor comparisons.",
)
VDYP_MISMATCH_LIMIT_OPTION = typer.Option(
    10,
    "--mismatch-limit",
    help="Maximum number of first-point mismatches to print.",
)
VDYP_MAX_CURVE_WARNINGS_OPTION = typer.Option(
    None,
    "--max-curve-warnings",
    help="Fail if curve warning events exceed this threshold.",
    show_default=False,
)
VDYP_MAX_FIRST_POINT_MISMATCHES_OPTION = typer.Option(
    None,
    "--max-first-point-mismatches",
    help="Fail if first-point mismatches exceed this threshold.",
    show_default=False,
)
VDYP_MAX_CURVE_PARSE_ERRORS_OPTION = typer.Option(
    None,
    "--max-curve-parse-errors",
    help="Fail if curve-log parse errors exceed this threshold.",
    show_default=False,
)
VDYP_MAX_RUN_PARSE_ERRORS_OPTION = typer.Option(
    None,
    "--max-run-parse-errors",
    help="Fail if run-log parse errors exceed this threshold.",
    show_default=False,
)
VDYP_MIN_CURVE_EVENTS_OPTION = typer.Option(
    None,
    "--min-curve-events",
    help="Fail if curve events are below this threshold.",
    show_default=False,
)
VDYP_MIN_RUN_EVENTS_OPTION = typer.Option(
    None,
    "--min-run-events",
    help="Fail if run events are below this threshold.",
    show_default=False,
)


def _preflight_checks(*, resume: bool) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    errors: list[str] = []
    warnings: list[str] = []

    data_root = repo_root / "data"
    if not data_root.exists():
        errors.append(f"Missing data directory: {data_root}")
    else:
        required_files = [
            data_root / "tsa_boundaries.feather",
            data_root / "ria_vri_vclr1p_checkpoint1.feather",
            data_root / "tipsy_params_columns",
        ]
        for path in required_files:
            if not path.exists():
                errors.append(f"Missing required file: {path}")

        optional_files = [
            data_root / "vdyp_ply.feather",
            data_root / "vdyp_lyr.feather",
            data_root / "vdyp_results.pkl",
        ]
        for path in optional_files:
            if not path.exists():
                warnings.append(f"Optional cache missing: {path}")

    maptiles_path = repo_root / "ria_maptiles.csv"
    if not maptiles_path.exists():
        warnings.append(f"Optional maptiles file missing: {maptiles_path}")

    vdyp_cfg = repo_root / "vdyp_io" / "VDYP_CFG"
    if not vdyp_cfg.exists():
        errors.append(f"Missing VDYP configuration directory: {vdyp_cfg}")

    vdyp_exe = repo_root / "VDYP7" / "VDYP7" / "VDYP7Console.exe"
    if not vdyp_exe.exists():
        errors.append(f"Missing VDYP executable: {vdyp_exe}")

    wine = shutil.which("wine")
    if not wine:
        if resume:
            warnings.append(
                "wine not found on PATH (resume may still work if caches exist)"
            )
        else:
            errors.append("wine not found on PATH (required to run VDYP)")

    for message in warnings:
        console.print(f"[yellow]Warning:[/yellow] {message}")

    if errors:
        for message in errors:
            console.print(f"[red]Error:[/red] {message}")
        raise typer.Exit(code=1)


def _enable_rich_tracebacks() -> None:
    try:
        from rich.traceback import install
    except Exception:
        return
    install(show_locals=True, width=140, extra_lines=2)


def _emit_stub(name: str) -> None:
    console.print(f"[yellow]Not implemented yet:[/yellow] {name}")
    console.print(
        "Use the legacy scripts (`00_data-prep.py`, `01a_run-tsa.py`, `01b_run-tsa.py`) for now."
    )
    raise typer.Exit(code=1)


@app.callback()
def main(
    version: bool = VERSION_OPTION,
    debug: bool = DEBUG_OPTION,
) -> None:
    if debug:
        _enable_rich_tracebacks()
    if version:
        typer.echo(__version__)
        raise typer.Exit()


@app.command("run")
def run_all(
    data_root: Path = DATA_ROOT_OPTION,
    output_root: Path = OUTPUT_ROOT_OPTION,
    tsa: list[str] | None = TSA_OPTION,
    resume: bool = RESUME_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    verbose: bool = VERBOSE_OPTION,
    skip_checks: bool = SKIP_CHECKS_OPTION,
    debug_rows: int | None = DEBUG_ROWS_OPTION,
    run_id: str | None = RUN_ID_OPTION,
    log_dir: Path = LOG_DIR_OPTION,
) -> None:
    if data_root != Path("data") or output_root != Path("outputs"):
        console.print("[red]data-root/output-root overrides are not wired yet.[/red]")
        raise typer.Exit(code=1)
    if dry_run:
        console.print(
            f"[yellow]Dry run:[/yellow] femic run tsa={tsa or 'ALL'} "
            f"resume={resume} debug_rows={debug_rows} run_id={run_id or 'AUTO'} "
            f"log_dir={log_dir}"
        )
        raise typer.Exit()
    if not skip_checks:
        _preflight_checks(resume=resume)
    if verbose:
        console.print(
            f"Running legacy pipeline for tsa={tsa or 'ALL'} (resume={resume}, "
            f"debug_rows={debug_rows}, run_id={run_id or 'AUTO'})"
        )
    manifest_path = run_data_prep(
        tsa,
        resume=resume,
        debug_rows=debug_rows,
        run_id=run_id,
        log_dir=log_dir,
    )
    console.print(f"Run manifest: {manifest_path}")


@prep_app.command("run")
def prep_run(
    data_root: Path = DATA_ROOT_OPTION,
    output_root: Path = OUTPUT_ROOT_OPTION,
    tsa: list[str] | None = TSA_OPTION,
    resume: bool = RESUME_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    _ = (data_root, output_root, tsa, resume, dry_run, verbose)
    _emit_stub("femic prep run")


@vdyp_app.command("run")
def vdyp_run(
    data_root: Path = DATA_ROOT_OPTION,
    output_root: Path = OUTPUT_ROOT_OPTION,
    tsa: list[str] | None = TSA_OPTION,
    resume: bool = RESUME_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    _ = (data_root, output_root, tsa, resume, dry_run, verbose)
    _emit_stub("femic vdyp run")


@vdyp_app.command("report")
def vdyp_report(
    curve_log: Path = VDYP_CURVE_LOG_OPTION,
    run_log: Path = VDYP_RUN_LOG_OPTION,
    expected_first_age: float = VDYP_EXPECTED_FIRST_AGE_OPTION,
    expected_first_volume: float = VDYP_EXPECTED_FIRST_VOLUME_OPTION,
    tolerance: float = VDYP_TOLERANCE_OPTION,
    mismatch_limit: int = VDYP_MISMATCH_LIMIT_OPTION,
    max_curve_warnings: int | None = VDYP_MAX_CURVE_WARNINGS_OPTION,
    max_first_point_mismatches: int | None = VDYP_MAX_FIRST_POINT_MISMATCHES_OPTION,
    max_curve_parse_errors: int | None = VDYP_MAX_CURVE_PARSE_ERRORS_OPTION,
    max_run_parse_errors: int | None = VDYP_MAX_RUN_PARSE_ERRORS_OPTION,
    min_curve_events: int | None = VDYP_MIN_CURVE_EVENTS_OPTION,
    min_run_events: int | None = VDYP_MIN_RUN_EVENTS_OPTION,
) -> None:
    summary = summarize_vdyp_logs(
        curve_log_path=curve_log,
        run_log_path=run_log,
        expected_first_age=expected_first_age,
        expected_first_volume=expected_first_volume,
        tolerance=tolerance,
        mismatch_limit=mismatch_limit,
    )
    console.print(f"Curve events: {summary.curve_events} ({curve_log})")
    console.print(f"Curve parse errors: {summary.curve_parse_errors}")
    console.print(f"Curve status counts: {summary.curve_status_counts}")
    console.print(f"Curve stage counts: {summary.curve_stage_counts}")
    console.print(f"Curve TSA counts: {summary.curve_tsa_counts}")
    console.print(f"Curve warning events: {summary.curve_warning_events}")
    console.print(
        "First-point checks: "
        f"events={summary.first_point_events} "
        f"matches={summary.first_point_matches} "
        f"mismatches={summary.first_point_mismatches}"
    )
    if summary.first_point_mismatch_rows:
        console.print("First-point mismatches (limited):")
        for row in summary.first_point_mismatch_rows:
            context = row.get("context")
            if not isinstance(context, dict):
                context = {}
            console.print(
                f"- tsa={context.get('tsa')} stratum={context.get('stratum_code')} "
                f"si={context.get('si_level')} "
                f"first_age={row.get('first_age')} first_volume={row.get('first_volume')} "
                f"status={row.get('status')} stage={row.get('stage')}"
            )

    console.print(f"Run events: {summary.run_events} ({run_log})")
    console.print(f"Run parse errors: {summary.run_parse_errors}")
    console.print(f"Run status counts: {summary.run_status_counts}")
    console.print(f"Run phase counts: {summary.run_phase_counts}")
    console.print(f"Run TSA counts: {summary.run_tsa_counts}")

    budget = VdypWarningBudget(
        max_curve_warnings=max_curve_warnings,
        max_first_point_mismatches=max_first_point_mismatches,
        max_curve_parse_errors=max_curve_parse_errors,
        max_run_parse_errors=max_run_parse_errors,
        min_curve_events=min_curve_events,
        min_run_events=min_run_events,
    )
    violations = evaluate_warning_budget(summary, budget)
    if violations:
        console.print("[red]VDYP warning-budget violations:[/red]")
        for violation in violations:
            console.print(f"- {violation}")
        raise typer.Exit(code=1)


@tsa_app.command("run")
def tsa_run(
    data_root: Path = DATA_ROOT_OPTION,
    output_root: Path = OUTPUT_ROOT_OPTION,
    tsa: list[str] | None = TSA_OPTION,
    resume: bool = RESUME_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    _ = (data_root, output_root, tsa, resume, dry_run, verbose)
    _emit_stub("femic tsa run")


app.add_typer(prep_app, name="prep")
app.add_typer(vdyp_app, name="vdyp")
app.add_typer(tsa_app, name="tsa")

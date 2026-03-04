"""Typer-based CLI entry point for FEMIC."""

from __future__ import annotations

import json
from pathlib import Path
import shutil

import typer
import yaml
from rich.console import Console

from femic import __version__
from femic.pipeline.io import (
    build_pipeline_run_config,
    file_sha256,
    load_pipeline_run_profile,
    resolve_effective_run_options,
)
from femic.pipeline.tipsy_config import (
    discover_tipsy_config_tsas,
    load_tipsy_tsa_config,
)
from femic.vdyp.reporting import (
    VdypWarningBudget,
    evaluate_warning_budget,
    summarize_vdyp_logs,
)
from femic.workflows.legacy import run_data_prep, run_post_tipsy_bundle

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
tipsy_app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Validate TIPSY config handoff files.",
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
RUN_CONFIG_OPTION = typer.Option(
    None,
    "--run-config",
    help="YAML/JSON run profile used to seed TSA/strata and mode defaults.",
    show_default=False,
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
    except (ModuleNotFoundError, ImportError):
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
    run_config: Path | None = RUN_CONFIG_OPTION,
) -> None:
    run_profile = None
    run_config_sha256: str | None = None
    if run_config is not None:
        try:
            run_profile = load_pipeline_run_profile(run_config)
            run_config_sha256 = file_sha256(run_config)
        except (
            FileNotFoundError,
            ValueError,
            json.JSONDecodeError,
            yaml.YAMLError,
        ) as exc:
            console.print(f"[red]Invalid run config:[/red] {exc}")
            raise typer.Exit(code=1) from exc
    effective = resolve_effective_run_options(
        tsa_list=tsa,
        resume=resume,
        dry_run=dry_run,
        verbose=verbose,
        skip_checks=skip_checks,
        debug_rows=debug_rows,
        run_id=run_id,
        log_dir=log_dir,
        profile=run_profile,
    )
    if effective.strata_list:
        console.print(
            "[yellow]Warning:[/yellow] run config strata selection is recorded but not "
            "yet wired into legacy execution filtering."
        )
    if data_root != Path("data") or output_root != Path("outputs"):
        console.print("[red]data-root/output-root overrides are not wired yet.[/red]")
        raise typer.Exit(code=1)
    if effective.dry_run:
        console.print(
            f"[yellow]Dry run:[/yellow] femic run tsa={effective.tsa_list or 'ALL'} "
            f"resume={effective.resume} debug_rows={effective.debug_rows} "
            f"run_id={effective.run_id or 'AUTO'} log_dir={effective.log_dir}"
        )
        raise typer.Exit()
    if not effective.skip_checks:
        _preflight_checks(resume=effective.resume)
    if effective.verbose:
        console.print(
            f"Running legacy pipeline for tsa={effective.tsa_list or 'ALL'} "
            f"(resume={effective.resume}, debug_rows={effective.debug_rows}, "
            f"run_id={effective.run_id or 'AUTO'})"
        )
    pipeline_run_config = build_pipeline_run_config(
        tsa_list=effective.tsa_list,
        resume=effective.resume,
        debug_rows=effective.debug_rows,
        run_id=effective.run_id,
        log_dir=effective.log_dir,
        output_root=output_root,
        run_config_path=run_config,
        run_config_sha256=run_config_sha256,
    )
    manifest_path = run_data_prep(pipeline_run_config)
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


@tsa_app.command("post-tipsy")
def tsa_post_tipsy(
    tsa: list[str] | None = TSA_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    targets = [str(v).zfill(2) for v in tsa] if tsa else []
    if not targets:
        console.print("[red]Provide at least one TSA via --tsa for post-tipsy.[/red]")
        raise typer.Exit(code=1)
    result = run_post_tipsy_bundle(
        tsa_list=targets,
        message_fn=console.print if verbose else (lambda *_args, **_kwargs: None),
    )
    console.print(
        f"[green]post-tipsy completed[/green] tsa={result.tsa_list} "
        f"au_rows={result.au_rows} curves={result.curve_rows} "
        f"curve_points={result.curve_points_rows}"
    )
    console.print(f"au_table: {result.au_table_path}")
    console.print(f"curve_table: {result.curve_table_path}")
    console.print(f"curve_points_table: {result.curve_points_table_path}")


@tipsy_app.command("validate")
def tipsy_validate(
    config_dir: Path = typer.Option(
        Path("config/tipsy"),
        "--config-dir",
        help="Directory containing tsaXX.yaml files.",
    ),
    tsa: list[str] | None = TSA_OPTION,
) -> None:
    found = discover_tipsy_config_tsas(config_dir)
    if not found:
        console.print(f"[red]No TIPSY configs found in {config_dir}[/red]")
        raise typer.Exit(code=1)
    targets = sorted({str(v).zfill(2) for v in tsa}) if tsa else sorted(found.keys())
    missing = [code for code in targets if code not in found]
    if missing:
        console.print(f"[red]Missing TSA config files:[/red] {', '.join(missing)}")
        raise typer.Exit(code=1)
    for code in targets:
        load_tipsy_tsa_config(tsa_code=code, config_dir=config_dir)
    console.print(
        f"[green]Validated TIPSY configs:[/green] {', '.join(targets)} "
        f"(dir={config_dir})"
    )


app.add_typer(prep_app, name="prep")
app.add_typer(vdyp_app, name="vdyp")
app.add_typer(tsa_app, name="tsa")
app.add_typer(tipsy_app, name="tipsy")

"""Patchworks runtime helpers for Wine + Matrix Builder execution."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import shlex
import subprocess
from typing import Any

import yaml

DEFAULT_LICENSE_ENV = "SPS_LICENSE_SERVER"
DEFAULT_PATCHWORKS_JAR_PATH = Path("reference/Patchworks/patchworks.jar")
DEFAULT_PATCHWORKS_CONFIG_PATH = Path("config/patchworks.runtime.yaml")
DEFAULT_PATCHWORKS_LOG_DIR = Path("vdyp_io/logs")
FATAL_MATRIX_STDERR_PATTERNS = (
    "no mrsidget2_64 in java.library.path",
    "not licensed or no connection to license server",
    "couldn't create component peer",
    "$display is set correctly",
    "sps home directory not found, installation not complete",
    "ip helper library getadaptersaddresses function failed",
)


@dataclass(frozen=True)
class PatchworksRuntimeConfig:
    """Resolved runtime settings for Patchworks execution."""

    config_path: Path
    jar_path: Path
    wine_prefix: Path | None
    license_env: str
    license_value: str
    spshome: str
    use_xvfb: bool
    fragments_path: Path
    matrix_output_dir: Path
    forestmodel_xml_path: Path


@dataclass(frozen=True)
class PatchworksPreflightResult:
    """Preflight report for Patchworks runtime execution."""

    config: PatchworksRuntimeConfig
    wine_executable: str | None
    license_host: str | None
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class PatchworksExecutionResult:
    """Execution outputs for a Wine-launched Patchworks command."""

    run_id: str
    command: tuple[str, ...]
    command_string: str
    returncode: int
    stdout_log_path: Path
    stderr_log_path: Path
    manifest_path: Path
    failures: tuple[str, ...]


class PatchworksConfigError(ValueError):
    """Invalid Patchworks runtime config."""


def _load_yaml_or_json(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        payload = json.loads(text)
    else:
        payload = yaml.safe_load(text)
    if not isinstance(payload, dict):
        raise PatchworksConfigError(
            f"Patchworks config must contain a top-level object: {path}"
        )
    return payload


def _as_path(value: Any, *, field: str, base_dir: Path) -> Path:
    if value is None or not str(value).strip():
        raise PatchworksConfigError(f"Missing required field: {field}")
    candidate = Path(str(value)).expanduser()
    if not candidate.is_absolute():
        candidate = base_dir / candidate
    return candidate.resolve()


def _as_optional_path(value: Any, *, base_dir: Path) -> Path | None:
    if value is None or not str(value).strip():
        return None
    candidate = Path(str(value)).expanduser()
    if not candidate.is_absolute():
        candidate = base_dir / candidate
    return candidate.resolve()


def load_patchworks_runtime_config(path: Path) -> PatchworksRuntimeConfig:
    """Load and validate Patchworks runtime YAML/JSON config."""

    resolved_path = path.expanduser().resolve()
    if not resolved_path.exists():
        raise FileNotFoundError(f"Patchworks config not found: {resolved_path}")

    payload = _load_yaml_or_json(resolved_path)
    patchworks = payload.get("patchworks")
    matrix_builder = payload.get("matrix_builder")
    if not isinstance(patchworks, dict):
        raise PatchworksConfigError("Missing required section: patchworks")
    if not isinstance(matrix_builder, dict):
        raise PatchworksConfigError("Missing required section: matrix_builder")

    base_dir = resolved_path.parent
    jar_path = _as_path(
        patchworks.get("jar_path", DEFAULT_PATCHWORKS_JAR_PATH),
        field="patchworks.jar_path",
        base_dir=base_dir,
    )
    wine_prefix = _as_optional_path(patchworks.get("wine_prefix"), base_dir=base_dir)

    license_env = str(patchworks.get("license_env", DEFAULT_LICENSE_ENV)).strip()
    if not license_env:
        raise PatchworksConfigError("patchworks.license_env must not be empty")

    license_value = str(
        patchworks.get("license_value", os.environ.get(license_env, ""))
    ).strip()
    if not license_value:
        raise PatchworksConfigError(
            "Missing license value: set patchworks.license_value or export "
            f"{license_env} in environment"
        )
    spshome = str(patchworks.get("spshome", os.environ.get("SPSHOME", ""))).strip()
    if not spshome:
        raise PatchworksConfigError(
            "Missing Patchworks install home: set patchworks.spshome or export SPSHOME"
        )
    use_xvfb = bool(patchworks.get("use_xvfb", False))

    fragments_path = _as_path(
        matrix_builder.get("fragments_path"),
        field="matrix_builder.fragments_path",
        base_dir=base_dir,
    )
    matrix_output_dir = _as_path(
        matrix_builder.get("output_dir"),
        field="matrix_builder.output_dir",
        base_dir=base_dir,
    )
    forestmodel_xml_path = _as_path(
        matrix_builder.get("forestmodel_xml_path"),
        field="matrix_builder.forestmodel_xml_path",
        base_dir=base_dir,
    )

    return PatchworksRuntimeConfig(
        config_path=resolved_path,
        jar_path=jar_path,
        wine_prefix=wine_prefix,
        license_env=license_env,
        license_value=license_value,
        spshome=spshome,
        use_xvfb=use_xvfb,
        fragments_path=fragments_path,
        matrix_output_dir=matrix_output_dir,
        forestmodel_xml_path=forestmodel_xml_path,
    )


def parse_license_server(value: str) -> tuple[str, str]:
    """Parse `user@server` license format."""

    normalized = value.strip()
    if "@" not in normalized:
        raise PatchworksConfigError(
            "License value must use '<username>@<server>' format"
        )
    username, host = normalized.split("@", 1)
    username = username.strip()
    host = host.strip()
    if not username or not host:
        raise PatchworksConfigError(
            "License value must include both username and server host"
        )
    return username, host


def find_wine_executable() -> str | None:
    """Return preferred wine executable path/name on PATH."""

    for candidate in ("wine64", "wine"):
        found = shutil_which(candidate)
        if found:
            return found
    return None


def shutil_which(name: str) -> str | None:
    """Wrapper for monkeypatch-friendly which lookup."""

    from shutil import which

    return which(name)


def to_wine_windows_path(path: Path) -> str:
    """Map absolute POSIX path to Wine's Z: drive path."""

    text = str(path)
    if len(text) >= 2 and text[1] == ":":
        return text
    normalized = str(path.expanduser().resolve())
    return "Z:" + normalized.replace("/", "\\")


def build_matrix_builder_command_string(config: PatchworksRuntimeConfig) -> str:
    """Build the Windows CMD command to run Matrix Builder."""

    jar_dir = to_wine_windows_path(config.jar_path.parent)
    fragments = to_wine_windows_path(config.fragments_path)
    output_dir = to_wine_windows_path(config.matrix_output_dir)
    forestmodel_xml = to_wine_windows_path(config.forestmodel_xml_path)
    spshome = config.spshome
    lib_dir = f"{spshome}\\lib"
    return (
        f"cd /d {jar_dir} && "
        f'set "SPSHOME={spshome}" && '
        f'set "PATH=%PATH%;{spshome};{lib_dir}" && '
        f'java -Djava.library.path="{lib_dir}" -jar patchworks.jar '
        "ca.spatial.tracks.builder.Process "
        f'"{fragments}" "{output_dir}" "{forestmodel_xml}"'
    )


def build_appchooser_command_string(config: PatchworksRuntimeConfig) -> str:
    """Build Windows CMD command to open Patchworks app chooser."""

    jar_dir = to_wine_windows_path(config.jar_path.parent)
    spshome = config.spshome
    lib_dir = f"{spshome}\\lib"
    return (
        f"cd /d {jar_dir} && "
        f'set "SPSHOME={spshome}" && '
        f'set "PATH=%PATH%;{spshome};{lib_dir}" && '
        f'java -Djava.library.path="{lib_dir}" -jar patchworks.jar'
    )


def run_patchworks_preflight(
    *,
    config: PatchworksRuntimeConfig,
) -> PatchworksPreflightResult:
    """Run preflight checks before Wine-based Patchworks execution."""

    errors: list[str] = []
    warnings: list[str] = []

    wine_executable = find_wine_executable()
    if wine_executable is None:
        errors.append("wine64/wine not found on PATH")

    if not config.jar_path.exists():
        errors.append(f"Patchworks jar not found: {config.jar_path}")

    if not config.fragments_path.exists():
        errors.append(f"Fragments dataset not found: {config.fragments_path}")

    if not config.forestmodel_xml_path.exists():
        errors.append(f"ForestModel XML not found: {config.forestmodel_xml_path}")

    license_host: str | None = None
    try:
        _, license_host = parse_license_server(config.license_value)
    except PatchworksConfigError as exc:
        errors.append(str(exc))

    if wine_executable is not None:
        java_check = subprocess.run(
            [wine_executable, "cmd", "/c", "java -version"],
            capture_output=True,
            text=True,
            env=_build_base_env(config),
            check=False,
        )
        if java_check.returncode != 0:
            errors.append(
                "Java runtime unavailable inside Wine context "
                "(command `java -version` failed)"
            )

    return PatchworksPreflightResult(
        config=config,
        wine_executable=wine_executable,
        license_host=license_host,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def _build_base_env(config: PatchworksRuntimeConfig) -> dict[str, str]:
    env = dict(os.environ)
    env[config.license_env] = config.license_value
    env["SPSHOME"] = config.spshome
    if config.wine_prefix is not None:
        env["WINEPREFIX"] = str(config.wine_prefix)
    return env


def _build_launch_command(
    *,
    wine_executable: str,
    command_string: str,
    use_xvfb: bool,
) -> tuple[str, ...]:
    command: tuple[str, ...] = (wine_executable, "cmd", "/c", command_string)
    if use_xvfb:
        xvfb_run = shutil_which("xvfb-run")
        if xvfb_run is None:
            raise PatchworksConfigError(
                "patchworks.use_xvfb=true but xvfb-run is not available on PATH"
            )
        command = (xvfb_run, "-a", *command)
    return command


def _matrix_output_ready(path: Path) -> bool:
    return path.exists() and any(path.iterdir())


def _detect_fatal_output(output_text: str) -> tuple[str, ...]:
    stderr_lower = output_text.lower()
    return tuple(
        pattern for pattern in FATAL_MATRIX_STDERR_PATTERNS if pattern in stderr_lower
    )


def _resolve_run_id(run_id: str | None) -> str:
    if run_id and run_id.strip():
        return run_id.strip()
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    return f"patchworks_{stamp}"


def run_patchworks_command(
    *,
    config: PatchworksRuntimeConfig,
    interactive: bool,
    log_dir: Path,
    run_id: str | None = None,
) -> PatchworksExecutionResult:
    """Execute Patchworks command under Wine and capture logs+manifest."""

    preflight = run_patchworks_preflight(config=config)
    if not preflight.ok:
        raise PatchworksConfigError(
            "Patchworks preflight failed prior to execution: "
            + "; ".join(preflight.errors)
        )
    assert preflight.wine_executable is not None

    effective_run_id = _resolve_run_id(run_id)
    resolved_log_dir = log_dir.expanduser().resolve()
    resolved_log_dir.mkdir(parents=True, exist_ok=True)

    stdout_log = (
        resolved_log_dir / f"patchworks_matrixbuilder_stdout-{effective_run_id}.log"
    )
    stderr_log = (
        resolved_log_dir / f"patchworks_matrixbuilder_stderr-{effective_run_id}.log"
    )
    manifest_path = (
        resolved_log_dir / f"patchworks_matrixbuilder_manifest-{effective_run_id}.json"
    )

    command_string = (
        build_appchooser_command_string(config)
        if interactive
        else build_matrix_builder_command_string(config)
    )
    command = _build_launch_command(
        wine_executable=preflight.wine_executable,
        command_string=command_string,
        use_xvfb=config.use_xvfb,
    )

    proc = subprocess.run(
        list(command),
        capture_output=True,
        text=True,
        env=_build_base_env(config),
        check=False,
    )

    stdout_log.write_text(proc.stdout or "", encoding="utf-8")
    stderr_log.write_text(proc.stderr or "", encoding="utf-8")

    failures: list[str] = []
    output_for_scan = (proc.stderr or "") + "\n" + (proc.stdout or "")
    fatal_stderr_matches = _detect_fatal_output(output_for_scan)
    if fatal_stderr_matches:
        failures.append(
            "fatal stderr signatures detected: " + ", ".join(fatal_stderr_matches)
        )
    if not interactive and not _matrix_output_ready(config.matrix_output_dir):
        failures.append(
            f"matrix output directory missing or empty: {config.matrix_output_dir}"
        )

    effective_returncode = proc.returncode if not failures else 1

    manifest_payload = {
        "run_id": effective_run_id,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "interactive": interactive,
        "command": list(command),
        "command_string": command_string,
        "returncode": effective_returncode,
        "runtime": {
            "wine_executable": preflight.wine_executable,
            "jar_path": str(config.jar_path),
            "license_env": config.license_env,
            "license_value": config.license_value,
            "spshome": config.spshome,
            "use_xvfb": config.use_xvfb,
            "wine_prefix": str(config.wine_prefix) if config.wine_prefix else None,
        },
        "inputs": {
            "fragments_path": str(config.fragments_path),
            "matrix_output_dir": str(config.matrix_output_dir),
            "forestmodel_xml_path": str(config.forestmodel_xml_path),
        },
        "logs": {
            "stdout": str(stdout_log),
            "stderr": str(stderr_log),
        },
        "failures": failures,
    }
    manifest_path.write_text(json.dumps(manifest_payload, indent=2), encoding="utf-8")

    return PatchworksExecutionResult(
        run_id=effective_run_id,
        command=command,
        command_string=command_string,
        returncode=effective_returncode,
        stdout_log_path=stdout_log,
        stderr_log_path=stderr_log,
        manifest_path=manifest_path,
        failures=tuple(failures),
    )


def format_command_for_display(command: tuple[str, ...]) -> str:
    """Return shell-quoted command for human-readable logs."""

    return " ".join(shlex.quote(part) for part in command)

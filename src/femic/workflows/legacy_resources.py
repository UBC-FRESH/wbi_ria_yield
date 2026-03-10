"""Helpers for resolving packaged legacy stage script resources."""

from __future__ import annotations

from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
import os
from importlib import resources
from pathlib import Path
from typing import Iterator


LEGACY_SCRIPT_PACKAGE = "femic.resources.legacy"
LEGACY_SCRIPT_ROOT_ENV = "FEMIC_LEGACY_SCRIPT_ROOT"
LEGACY_SCRIPT_FILENAMES: tuple[str, ...] = (
    "00_data-prep.py",
    "01a_run-tsa.py",
    "01b_run-tsa.py",
)


@dataclass(frozen=True)
class LegacyScriptBundle:
    """Resolved paths to legacy script trio required by stage execution."""

    script_root: Path
    stage00_path: Path
    stage01a_path: Path
    stage01b_path: Path
    source: str


def _validate_legacy_script_root(root: Path) -> LegacyScriptBundle:
    resolved = root.expanduser().resolve()
    missing = [
        filename
        for filename in LEGACY_SCRIPT_FILENAMES
        if not (resolved / filename).is_file()
    ]
    if missing:
        missing_csv = ", ".join(missing)
        raise FileNotFoundError(
            f"Legacy script root missing required files ({missing_csv}): {resolved}"
        )
    return LegacyScriptBundle(
        script_root=resolved,
        stage00_path=resolved / "00_data-prep.py",
        stage01a_path=resolved / "01a_run-tsa.py",
        stage01b_path=resolved / "01b_run-tsa.py",
        source="filesystem",
    )


@contextmanager
def resolve_legacy_script_bundle(
    *,
    explicit_root: Path | None = None,
) -> Iterator[LegacyScriptBundle]:
    """Yield filesystem paths for legacy scripts from override or package resources."""
    if explicit_root is not None:
        yield _validate_legacy_script_root(explicit_root)
        return

    env_root = os.environ.get(LEGACY_SCRIPT_ROOT_ENV, "").strip()
    if env_root:
        yield _validate_legacy_script_root(Path(env_root))
        return

    with ExitStack() as stack:
        resolved: dict[str, Path] = {}
        for filename in LEGACY_SCRIPT_FILENAMES:
            resource = resources.files(LEGACY_SCRIPT_PACKAGE).joinpath(filename)
            file_path = stack.enter_context(resources.as_file(resource))
            resolved[filename] = file_path
        bundle = LegacyScriptBundle(
            script_root=resolved["00_data-prep.py"].parent.resolve(),
            stage00_path=resolved["00_data-prep.py"].resolve(),
            stage01a_path=resolved["01a_run-tsa.py"].resolve(),
            stage01b_path=resolved["01b_run-tsa.py"].resolve(),
            source="package",
        )
        yield bundle

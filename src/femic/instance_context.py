"""Instance-root resolution helpers for deployment-scoped FEMIC execution."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Mapping


INSTANCE_ROOT_ENV = "FEMIC_INSTANCE_ROOT"

_LEGACY_WORKSPACE_MARKERS: tuple[Path, ...] = (
    Path("00_data-prep.py"),
    Path("config/run_profile.case_template.yaml"),
    Path("config/tipsy/template.case.yaml"),
)
_INSTANCE_MARKERS: tuple[Path, ...] = (
    Path("config"),
    Path("data"),
)


@dataclass(frozen=True)
class InstanceContext:
    """Resolved instance-root context used for path derivation."""

    root: Path
    source: str
    warnings: tuple[str, ...] = ()

    def resolve_path(self, value: Path) -> Path:
        """Resolve user-provided path relative to the instance root."""
        if not isinstance(value, Path):
            default_value = getattr(value, "default", None)
            if isinstance(default_value, Path):
                value = default_value
            else:
                raise TypeError(f"Expected Path-like value, got {type(value)!r}")
        candidate = value.expanduser()
        if candidate.is_absolute():
            return candidate.resolve()
        return (self.root / candidate).resolve()


def _looks_like_legacy_workspace(path: Path) -> bool:
    return all((path / marker).exists() for marker in _LEGACY_WORKSPACE_MARKERS)


def _looks_like_instance_root(path: Path) -> bool:
    return any((path / marker).exists() for marker in _INSTANCE_MARKERS)


def resolve_instance_context(
    *,
    instance_root: Path | None,
    env: Mapping[str, str] | None = None,
    cwd: Path | None = None,
    legacy_repo_root: Path | None = None,
    allow_legacy_fallback: bool = True,
) -> InstanceContext:
    """Resolve active instance root with CLI > env > cwd precedence."""
    active_env = os.environ if env is None else env
    resolved_cwd = (cwd or Path.cwd()).expanduser().resolve()

    # Typer OptionInfo objects can surface when command functions are invoked
    # directly in tests without passing optional parameters.
    if instance_root is not None and not isinstance(instance_root, Path):
        instance_root = None

    if instance_root is not None:
        return InstanceContext(
            root=instance_root.expanduser().resolve(),
            source="cli",
        )

    env_root_raw = active_env.get(INSTANCE_ROOT_ENV, "").strip()
    if env_root_raw:
        return InstanceContext(
            root=Path(env_root_raw).expanduser().resolve(),
            source="env",
        )

    warnings: list[str] = []
    if allow_legacy_fallback and legacy_repo_root is not None:
        resolved_legacy = legacy_repo_root.expanduser().resolve()
        if (
            resolved_cwd != resolved_legacy
            and _looks_like_legacy_workspace(resolved_legacy)
            and not _looks_like_instance_root(resolved_cwd)
        ):
            warnings.append(
                "Using legacy repository root as instance root for compatibility. "
                "Set --instance-root or FEMIC_INSTANCE_ROOT to silence this warning."
            )
            return InstanceContext(
                root=resolved_legacy,
                source="legacy",
                warnings=tuple(warnings),
            )

    return InstanceContext(root=resolved_cwd, source="cwd", warnings=tuple(warnings))

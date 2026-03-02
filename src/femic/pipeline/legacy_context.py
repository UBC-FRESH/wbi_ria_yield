"""Helpers for explicit legacy notebook-module context binding."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from types import ModuleType
from typing import Any

RUN_01A_CONTEXT_SYMBOLS: tuple[str, ...] = ()

RUN_01B_CONTEXT_SYMBOLS: tuple[str, ...] = ()


def bind_legacy_module_context(
    *,
    module: ModuleType,
    available_symbols: Mapping[str, Any],
    required_symbols: Sequence[str],
) -> None:
    """Bind required context symbols into a legacy module namespace."""
    missing = [name for name in required_symbols if name not in available_symbols]
    if missing:
        missing_joined = ", ".join(sorted(missing))
        raise RuntimeError(
            f"Missing required legacy context symbols for {module.__name__}: "
            f"{missing_joined}"
        )
    for name in required_symbols:
        module.__dict__[name] = available_symbols[name]

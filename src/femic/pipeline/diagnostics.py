"""Shared diagnostics formatting helpers for legacy pipeline/runtime errors."""

from __future__ import annotations

from typing import Any, Mapping


def format_context_kv(
    *,
    context: Mapping[str, Any],
    skip_none: bool = True,
) -> str:
    """Format context mapping as stable `key=value` pairs for error diagnostics."""
    parts: list[str] = []
    for key, value in context.items():
        if skip_none and value is None:
            continue
        parts.append(f"{key}={value}")
    return ", ".join(parts)


def build_contextual_error_message(
    *,
    prefix: str,
    context: Mapping[str, Any],
    skip_none: bool = True,
) -> str:
    """Build a human-readable diagnostic message with optional key/value context."""
    details = format_context_kv(context=context, skip_none=skip_none)
    if not details:
        return prefix
    return f"{prefix}: {details}"

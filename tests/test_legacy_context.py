from __future__ import annotations

import types

import pytest

from femic.pipeline.legacy_context import (
    RUN_01A_CONTEXT_SYMBOLS,
    RUN_01B_CONTEXT_SYMBOLS,
    bind_legacy_module_context,
)


def test_bind_legacy_module_context_sets_required_symbols() -> None:
    module = types.ModuleType("legacy_test_module")
    available = {"alpha": 1, "beta": {"x": 2}}

    bind_legacy_module_context(
        module=module,
        available_symbols=available,
        required_symbols=("alpha", "beta"),
    )

    assert module.alpha == 1
    assert module.beta == {"x": 2}


def test_bind_legacy_module_context_raises_on_missing_symbols() -> None:
    module = types.ModuleType("legacy_test_module")
    available = {"alpha": 1}

    with pytest.raises(RuntimeError, match="Missing required legacy context symbols"):
        bind_legacy_module_context(
            module=module,
            available_symbols=available,
            required_symbols=("alpha", "gamma"),
        )


def test_run_context_symbol_lists_are_empty() -> None:
    assert RUN_01A_CONTEXT_SYMBOLS == ()
    assert RUN_01B_CONTEXT_SYMBOLS == ()


def test_bind_legacy_module_context_allows_empty_required_symbols() -> None:
    module = types.ModuleType("legacy_test_module")
    bind_legacy_module_context(
        module=module,
        available_symbols={"alpha": 1},
        required_symbols=(),
    )
    assert not hasattr(module, "alpha")

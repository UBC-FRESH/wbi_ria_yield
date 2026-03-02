from __future__ import annotations

import builtins

import pytest

from femic.cli import main as cli_main


def test_enable_rich_tracebacks_ignores_missing_rich(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import = builtins.__import__

    def _patched_import(
        name: str,
        globals: object = None,
        locals: object = None,
        fromlist: object = (),
        level: int = 0,
    ) -> object:
        if name == "rich.traceback":
            raise ModuleNotFoundError("rich not installed")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _patched_import)
    cli_main._enable_rich_tracebacks()


def test_enable_rich_tracebacks_unexpected_import_error_propagates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import = builtins.__import__

    def _patched_import(
        name: str,
        globals: object = None,
        locals: object = None,
        fromlist: object = (),
        level: int = 0,
    ) -> object:
        if name == "rich.traceback":
            raise ZeroDivisionError("unexpected")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _patched_import)
    with pytest.raises(ZeroDivisionError, match="unexpected"):
        cli_main._enable_rich_tracebacks()

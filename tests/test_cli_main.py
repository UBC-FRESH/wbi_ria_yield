from __future__ import annotations

import builtins
from pathlib import Path

import pytest
import typer

from femic.cli import main as cli_main


def _set_cli_repo_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    fake_module_path = repo_root / "src" / "femic" / "cli" / "main.py"
    fake_module_path.parent.mkdir(parents=True, exist_ok=True)
    fake_module_path.write_text("# fake module path for preflight tests\n")
    monkeypatch.setattr(cli_main, "__file__", str(fake_module_path))
    return repo_root


def _create_preflight_required_layout(repo_root: Path) -> None:
    data_root = repo_root / "data"
    data_root.mkdir(parents=True, exist_ok=True)
    (data_root / "tsa_boundaries.feather").touch()
    (data_root / "ria_vri_vclr1p_checkpoint1.feather").touch()
    (data_root / "tipsy_params_columns").touch()
    (data_root / "vdyp_ply.feather").touch()
    (data_root / "vdyp_lyr.feather").touch()
    (data_root / "vdyp_results.pkl").touch()

    (repo_root / "ria_maptiles.csv").touch()

    vdyp_cfg = repo_root / "vdyp_io" / "VDYP_CFG"
    vdyp_cfg.mkdir(parents=True, exist_ok=True)

    vdyp_exe = repo_root / "VDYP7" / "VDYP7" / "VDYP7Console.exe"
    vdyp_exe.parent.mkdir(parents=True, exist_ok=True)
    vdyp_exe.touch()


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


def test_preflight_checks_exit_when_data_root_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _set_cli_repo_root(monkeypatch, tmp_path)
    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)
    monkeypatch.setattr(cli_main.shutil, "which", lambda _: "/usr/bin/wine")

    with pytest.raises(typer.Exit) as exc_info:
        cli_main._preflight_checks(resume=False)

    assert exc_info.value.exit_code == 1
    assert any("Missing data directory" in msg for msg in messages)


def test_preflight_checks_resume_warns_when_wine_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo_root = _set_cli_repo_root(monkeypatch, tmp_path)
    _create_preflight_required_layout(repo_root)

    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)
    monkeypatch.setattr(cli_main.shutil, "which", lambda _: None)

    cli_main._preflight_checks(resume=True)

    assert any("wine not found on PATH" in msg for msg in messages)
    assert not any("[red]Error:" in msg for msg in messages)


def test_preflight_checks_fails_for_specific_missing_required_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo_root = _set_cli_repo_root(monkeypatch, tmp_path)
    _create_preflight_required_layout(repo_root)
    missing_required = repo_root / "data" / "tipsy_params_columns"
    missing_required.unlink()

    messages: list[str] = []
    monkeypatch.setattr(cli_main.console, "print", messages.append)
    monkeypatch.setattr(cli_main.shutil, "which", lambda _: "/usr/bin/wine")

    with pytest.raises(typer.Exit) as exc_info:
        cli_main._preflight_checks(resume=False)

    assert exc_info.value.exit_code == 1
    error_messages = [msg for msg in messages if "[red]Error:" in msg]
    assert len(error_messages) == 1
    assert "Missing required file" in error_messages[0]
    assert str(missing_required) in error_messages[0]

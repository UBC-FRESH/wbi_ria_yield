from __future__ import annotations

from pathlib import Path

from femic.instance_context import (
    INSTANCE_ROOT_ENV,
    resolve_instance_context,
)


def test_resolve_instance_context_prefers_cli_value(tmp_path: Path) -> None:
    cli_root = tmp_path / "cli"
    ctx = resolve_instance_context(
        instance_root=cli_root,
        env={},
        cwd=tmp_path / "cwd",
        legacy_repo_root=None,
    )
    assert ctx.root == cli_root.resolve()
    assert ctx.source == "cli"


def test_resolve_instance_context_uses_env_when_cli_missing(tmp_path: Path) -> None:
    env_root = tmp_path / "from_env"
    ctx = resolve_instance_context(
        instance_root=None,
        env={INSTANCE_ROOT_ENV: str(env_root)},
        cwd=tmp_path / "cwd",
        legacy_repo_root=None,
    )
    assert ctx.root == env_root.resolve()
    assert ctx.source == "env"


def test_resolve_instance_context_defaults_to_cwd(tmp_path: Path) -> None:
    cwd_root = tmp_path / "workspace"
    cwd_root.mkdir(parents=True)
    ctx = resolve_instance_context(
        instance_root=None,
        env={},
        cwd=cwd_root,
        legacy_repo_root=None,
    )
    assert ctx.root == cwd_root.resolve()
    assert ctx.source == "cwd"


def test_resolve_instance_context_legacy_fallback_warns(tmp_path: Path) -> None:
    cwd_root = tmp_path / "empty"
    cwd_root.mkdir(parents=True)
    legacy_root = tmp_path / "legacy"
    (legacy_root / "config/tipsy").mkdir(parents=True)
    (legacy_root / "00_data-prep.py").write_text("# legacy", encoding="utf-8")
    (legacy_root / "config/run_profile.case_template.yaml").write_text(
        "selection: {}\n",
        encoding="utf-8",
    )
    (legacy_root / "config/tipsy/template.case.yaml").write_text(
        "rules: []\n",
        encoding="utf-8",
    )

    ctx = resolve_instance_context(
        instance_root=None,
        env={},
        cwd=cwd_root,
        legacy_repo_root=legacy_root,
        allow_legacy_fallback=True,
    )

    assert ctx.root == legacy_root.resolve()
    assert ctx.source == "legacy"
    assert ctx.warnings

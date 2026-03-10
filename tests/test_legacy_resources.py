from __future__ import annotations

from pathlib import Path

import pytest

from femic.workflows.legacy_resources import (
    LEGACY_SCRIPT_FILENAMES,
    resolve_legacy_script_bundle,
)


def test_resolve_legacy_script_bundle_from_package() -> None:
    with resolve_legacy_script_bundle(explicit_root=None) as bundle:
        assert bundle.source == "package"
        assert bundle.stage00_path.is_file()
        assert bundle.stage01a_path.is_file()
        assert bundle.stage01b_path.is_file()


def test_resolve_legacy_script_bundle_explicit_root_validation(tmp_path: Path) -> None:
    script_root = tmp_path / "legacy"
    script_root.mkdir(parents=True)
    for name in LEGACY_SCRIPT_FILENAMES[:-1]:
        (script_root / name).write_text("# stub\n", encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        with resolve_legacy_script_bundle(explicit_root=script_root):
            pass

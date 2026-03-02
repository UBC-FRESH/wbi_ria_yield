from __future__ import annotations

import ast
from pathlib import Path


def _load_legacy_orchestration_tree() -> ast.AST:
    source_path = Path(__file__).resolve().parents[1] / "00_data-prep.py"
    return ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))


def _find_method_calls(
    tree: ast.AST, module_name: str, method_name: str
) -> list[ast.Call]:
    calls: list[ast.Call] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute):
            continue
        if func.attr != method_name:
            continue
        if isinstance(func.value, ast.Name) and func.value.id == module_name:
            calls.append(node)
    return calls


def test_run01a_call_uses_explicit_keyword_handoff() -> None:
    tree = _load_legacy_orchestration_tree()
    calls = _find_method_calls(
        tree, module_name="_run01a_module", method_name="run_tsa"
    )
    assert len(calls) == 1
    kwargs = {kw.arg for kw in calls[0].keywords if kw.arg is not None}
    expected = {
        "tsa",
        "stratum_col",
        "f",
        "si_levels",
        "results",
        "vdyp_results",
        "vdyp_curves_smooth",
        "scsi_au",
        "au_scsi",
        "tipsy_params",
        "si_levelquants",
        "species_list",
        "runtime_config",
    }
    assert kwargs == expected


def test_run01a_call_passes_runtime_config_variable() -> None:
    tree = _load_legacy_orchestration_tree()
    calls = _find_method_calls(
        tree, module_name="_run01a_module", method_name="run_tsa"
    )
    assert len(calls) == 1
    kwarg_nodes = {kw.arg: kw.value for kw in calls[0].keywords if kw.arg is not None}
    runtime_value = kwarg_nodes["runtime_config"]
    assert isinstance(runtime_value, ast.Name)
    assert runtime_value.id == "runtime_config"


def test_run01b_call_uses_explicit_keyword_handoff() -> None:
    tree = _load_legacy_orchestration_tree()
    calls = _find_method_calls(
        tree, module_name="_run01b_module", method_name="run_tsa"
    )
    assert len(calls) == 1
    kwargs = {kw.arg for kw in calls[0].keywords if kw.arg is not None}
    assert kwargs == {"tsa", "results", "au_scsi", "tipsy_curves", "vdyp_curves_smooth"}


def test_no_context_binder_call_remains_in_legacy_orchestration() -> None:
    tree = _load_legacy_orchestration_tree()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "bind_legacy_module_context":
            raise AssertionError(
                "bind_legacy_module_context call should not be present"
            )


def test_legacy_orchestration_uses_shared_stage_loop_and_loader_helpers() -> None:
    tree = _load_legacy_orchestration_tree()
    loader_calls = 0
    loop_calls = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "load_legacy_module":
            loader_calls += 1
        if isinstance(func, ast.Name) and func.id == "run_legacy_tsa_loop":
            loop_calls += 1
    assert loader_calls == 2
    assert loop_calls == 2

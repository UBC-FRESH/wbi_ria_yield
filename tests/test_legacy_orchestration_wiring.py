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
        "resume_effective",
        "force_run_vdyp",
        "kwarg_overrides_for_tsa",
        "results",
        "vdyp_results",
        "vdyp_curves_smooth",
        "scsi_au",
        "au_scsi",
        "tipsy_params",
        "si_levelquants",
        "species_list",
        "vdyp_results_tsa_pickle_path_prefix",
        "vdyp_results_pickle_path",
        "vdyp_input_pandl_path",
        "vdyp_ply_feather_path",
        "vdyp_lyr_feather_path",
        "vdyp_curves_smooth_tsa_feather_path_prefix",
        "tipsy_params_columns",
        "tipsy_params_path_prefix",
        "vdyp_out_cache",
        "curve_fit_impl",
    }
    assert kwargs == expected


def test_run01a_call_uses_internal_vdyp_override_defaults() -> None:
    tree = _load_legacy_orchestration_tree()
    calls = _find_method_calls(
        tree, module_name="_run01a_module", method_name="run_tsa"
    )
    assert len(calls) == 1
    kwarg_nodes = {kw.arg: kw.value for kw in calls[0].keywords if kw.arg is not None}
    override_value = kwarg_nodes["kwarg_overrides_for_tsa"]
    assert isinstance(override_value, ast.Constant)
    assert override_value.value is None


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

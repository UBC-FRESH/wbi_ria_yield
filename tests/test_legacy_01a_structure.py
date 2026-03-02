from __future__ import annotations

import ast
from pathlib import Path


def _load_run01a_tree() -> ast.AST:
    source_path = Path(__file__).resolve().parents[1] / "01a_run-tsa.py"
    return ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))


def _run_tsa_function(tree: ast.AST) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_tsa":
            return node
    raise AssertionError("run_tsa function not found in 01a_run-tsa.py")


def test_run01a_uses_build_strata_summary_helper_call() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "build_strata_summary":
            return
    raise AssertionError("run_tsa should call build_strata_summary(...)")


def test_run01a_no_inline_target_nstrata_dict_assignment() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, ast.Dict):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "target_nstrata":
                raise AssertionError(
                    "run_tsa should not assign inline target_nstrata dict"
                )


def test_run01a_no_local_si_levels_reassignment() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "si_levels":
                raise AssertionError("run_tsa should not reassign si_levels locally")


def test_run01a_uses_lexmatch_alias_helper_call() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "build_stratum_lexmatch_alias_map":
            return
    raise AssertionError("run_tsa should call build_stratum_lexmatch_alias_map(...)")


def test_run01a_uses_apply_stratum_alias_map_helper_call() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "apply_stratum_alias_map":
            return
    raise AssertionError("run_tsa should call apply_stratum_alias_map(...)")


def test_run01a_has_no_nested_match_stratum_definition() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in run_tsa.body:
        if isinstance(node, ast.FunctionDef) and node.name == "match_stratum":
            raise AssertionError("run_tsa should not define nested match_stratum")


def test_run01a_uses_build_fit_stratum_curves_runner_helper_call() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "build_fit_stratum_curves_runner":
            return
    raise AssertionError("run_tsa should call build_fit_stratum_curves_runner(...)")


def test_run01a_no_direct_fit_stratum_curves_call() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "fit_stratum_curves":
            raise AssertionError(
                "run_tsa should use build_fit_stratum_curves_runner, not call fit_stratum_curves directly"
            )


def test_run01a_has_no_nested_fit_stratum_definition() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in run_tsa.body:
        if isinstance(node, ast.FunctionDef) and node.name == "fit_stratum":
            raise AssertionError("run_tsa should not define nested fit_stratum")


def test_run01a_has_no_nested_legacy_fit_function_definitions() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    forbidden = {
        "fit_func1",
        "fit_func1_bounds_func",
        "fit_func2",
        "fit_func2_bounds_func",
    }
    for node in run_tsa.body:
        if isinstance(node, ast.FunctionDef) and node.name in forbidden:
            raise AssertionError(
                "run_tsa should source legacy fit functions from pipeline helpers"
            )


def test_run01a_has_no_local_legacy_fit2_assignments() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    forbidden = {"fit_func2", "fit_func2_bounds_func"}
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in forbidden:
                raise AssertionError(
                    "run_tsa should not assign local legacy fit_func2 bindings"
                )


def test_run01a_uses_compile_strata_fit_results_helper_call() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "compile_strata_fit_results":
            return
    raise AssertionError("run_tsa should call compile_strata_fit_results(...)")


def test_run01a_no_inline_compile_one_lambda() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Name) and func.id == "compile_strata_fit_results"):
            continue
        for keyword in node.keywords:
            if keyword.arg == "compile_one_fn" and isinstance(
                keyword.value, ast.Lambda
            ):
                raise AssertionError(
                    "run_tsa should pass pre-built compile_one_fn, not inline lambda"
                )


def test_run01a_no_direct_run_vdyp_sampling_call() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "run_vdyp_sampling":
            raise AssertionError(
                "run_tsa should delegate via run_vdyp_for_stratum, not call run_vdyp_sampling directly"
            )


def test_run01a_uses_build_run_vdyp_for_stratum_runner_helper_call() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (
            isinstance(func, ast.Name)
            and func.id == "build_run_vdyp_for_stratum_runner"
        ):
            return
    raise AssertionError("run_tsa should call build_run_vdyp_for_stratum_runner(...)")


def test_run01a_no_direct_run_vdyp_for_stratum_call() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "run_vdyp_for_stratum":
            raise AssertionError(
                "run_tsa should use build_run_vdyp_for_stratum_runner, not call run_vdyp_for_stratum directly"
            )


def test_run01a_uses_build_bootstrap_vdyp_results_runner_helper_call() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (
            isinstance(func, ast.Name)
            and func.id == "build_bootstrap_vdyp_results_runner"
        ):
            return
    raise AssertionError("run_tsa should call build_bootstrap_vdyp_results_runner(...)")


def test_run01a_uses_build_curve_smoothing_plot_config_helper_call() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (
            isinstance(func, ast.Name)
            and func.id == "build_curve_smoothing_plot_config"
        ):
            return
    raise AssertionError("run_tsa should call build_curve_smoothing_plot_config(...)")


def test_run01a_no_inline_smoothing_plot_constant_assignments() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    forbidden = {"palette_flavours", "alphas"}
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in forbidden:
                raise AssertionError(
                    "run_tsa should source smoothing plot defaults from stage helper"
                )


def test_run01a_no_inline_tipsy_stage_constant_assignments() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    forbidden = {"min_operable_years", "si_iqrlo_quantile"}
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in forbidden:
                raise AssertionError(
                    "run_tsa should rely on shared helper defaults for TIPSY stage constants"
                )


def test_run01a_uses_default_tipsy_stage_kwargs() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Name) and func.id == "build_tipsy_params_for_tsa"):
            continue
        for keyword in node.keywords:
            if keyword.arg in {"min_operable_years", "si_iqrlo_quantile", "verbose"}:
                raise AssertionError(
                    "run_tsa should not override build_tipsy_params_for_tsa defaults"
                )
        return
    raise AssertionError("run_tsa should call build_tipsy_params_for_tsa(...)")


def test_run01a_no_inline_run_bootstrap_lambda() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (
            isinstance(func, ast.Name) and func.id == "load_or_build_vdyp_results_tsa"
        ):
            continue
        for keyword in node.keywords:
            if keyword.arg == "run_bootstrap_fn" and isinstance(
                keyword.value, ast.Lambda
            ):
                raise AssertionError(
                    "run_tsa should pass pre-built run_bootstrap_fn, not inline lambda"
                )


def test_run01a_has_no_nested_run_vdyp_definition() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in run_tsa.body:
        if isinstance(node, ast.FunctionDef) and node.name == "run_vdyp":
            raise AssertionError("run_tsa should not define nested run_vdyp")

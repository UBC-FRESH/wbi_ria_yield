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


def test_run01a_uses_target_nstrata_helper_call() -> None:
    tree = _load_run01a_tree()
    run_tsa = _run_tsa_function(tree)
    for node in ast.walk(run_tsa):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "target_nstrata_for":
            return
    raise AssertionError("run_tsa should call target_nstrata_for(...)")


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

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

import pandas as pd
import pytest

from femic.pipeline.vdyp_stage import (
    SmoothedCurveResult,
    build_curve_fit_adapter,
    build_smoothed_curve_table,
    execute_bootstrap_vdyp_runs,
    execute_curve_smoothing_runs,
    execute_vdyp_batch,
    load_vdyp_input_tables,
    load_or_build_vdyp_results_tsa,
    plot_curve_overlays,
)


@dataclass
class _RunResult:
    stdout: str
    stderr: str
    returncode: int = 0


def _sample_vdyp_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    vdyp_ply = pd.DataFrame({"FEATURE_ID": [1, 2, 3], "A": [10, 20, 30]})
    vdyp_lyr = pd.DataFrame({"FEATURE_ID": [1, 2, 3], "B": [100, 200, 300]})
    return vdyp_ply, vdyp_lyr


def test_build_curve_fit_adapter_converts_maxfev_to_max_nfev() -> None:
    captured: dict[str, object] = {}

    def fake_curve_fit(*_args: object, **kwargs: object) -> str:
        captured.update(kwargs)
        return "ok"

    class _FakeNumpy:
        @staticmethod
        def any(value: object) -> bool:
            if isinstance(value, (list, tuple)):
                return any(bool(v) for v in value)
            return bool(value)

        @staticmethod
        def isfinite(bounds: object) -> object:
            return bounds

    wrapped = build_curve_fit_adapter(
        curve_fit_impl=fake_curve_fit,
        np_module=_FakeNumpy(),
    )
    result = wrapped(bounds=(0.0, 1.0), maxfev=123)

    assert result == "ok"
    assert captured["max_nfev"] == 123
    assert "maxfev" not in captured


def test_build_curve_fit_adapter_keeps_existing_max_nfev() -> None:
    captured: dict[str, object] = {}

    def fake_curve_fit(*_args: object, **kwargs: object) -> str:
        captured.update(kwargs)
        return "ok"

    class _FakeNumpy:
        @staticmethod
        def any(value: object) -> bool:
            if isinstance(value, (list, tuple)):
                return any(bool(v) for v in value)
            return bool(value)

        @staticmethod
        def isfinite(bounds: object) -> object:
            return bounds

    wrapped = build_curve_fit_adapter(
        curve_fit_impl=fake_curve_fit,
        np_module=_FakeNumpy(),
    )
    wrapped(bounds=(0.0, 1.0), maxfev=111, max_nfev=222)

    assert captured["max_nfev"] == 222
    assert captured["maxfev"] == 111


def test_execute_vdyp_batch_logs_ok_and_returns_output(tmp_path: Path) -> None:
    (tmp_path / "vdyp_io").mkdir(parents=True)
    vdyp_ply, vdyp_lyr = _sample_vdyp_tables()
    events: list[dict[str, object]] = []
    text_logs: list[tuple[str, str]] = []

    def fake_write(*args: object) -> None:
        assert len(args) == 4

    def fake_import(path: str) -> dict[int, object]:
        assert Path(path).name.endswith(".out")
        return {1: {"curve": "ok"}}

    def fake_append_jsonl(path: str | Path, payload: object) -> None:
        assert path == tmp_path / "vdyp_io" / "vdyp_runs.jsonl"
        assert isinstance(payload, dict)
        events.append(payload)

    def fake_append_text(path: str | Path, text: str) -> None:
        text_logs.append((str(path), text))

    def fake_run(*_args: object, **_kwargs: object) -> _RunResult:
        return _RunResult(stdout="vdyp stdout", stderr="")

    out = execute_vdyp_batch(
        feature_ids=[1, 2],
        vdyp_ply=vdyp_ply,
        vdyp_lyr=vdyp_lyr,
        vdyp_binpath="VDYP7/VDYP7/VDYP7Console.exe",
        vdyp_params_infile="vdyp_params-landp",
        vdyp_io_dirname=str(tmp_path / "vdyp_io"),
        vdyp_log_path=tmp_path / "vdyp_io" / "vdyp_runs.jsonl",
        vdyp_stdout_log_path=tmp_path / "vdyp_io" / "vdyp_stdout.log",
        vdyp_stderr_log_path=tmp_path / "vdyp_io" / "vdyp_stderr.log",
        phase="initial",
        cache_hits=1,
        timeout=10,
        run_id="run-abc",
        base_context={"tsa": "08"},
        write_vdyp_infiles=fake_write,
        import_vdyp_tables_fn=fake_import,
        append_jsonl_fn=fake_append_jsonl,
        append_text_fn=fake_append_text,
        subprocess_run=fake_run,
    )

    assert out == {1: {"curve": "ok"}}
    assert len(events) == 1
    assert events[0]["status"] == "ok"
    assert events[0]["phase"] == "initial"
    assert events[0]["context"] == {"tsa": "08", "run_id": "run-abc"}
    assert len(text_logs) == 1
    assert "phase=initial" in text_logs[0][1]


def test_execute_vdyp_batch_logs_parse_error(tmp_path: Path) -> None:
    (tmp_path / "vdyp_io").mkdir(parents=True)
    vdyp_ply, vdyp_lyr = _sample_vdyp_tables()
    events: list[dict[str, object]] = []

    def fake_append_jsonl(_path: str | Path, payload: object) -> None:
        assert isinstance(payload, dict)
        events.append(payload)

    out = execute_vdyp_batch(
        feature_ids=[1],
        vdyp_ply=vdyp_ply,
        vdyp_lyr=vdyp_lyr,
        vdyp_binpath="VDYP7/VDYP7/VDYP7Console.exe",
        vdyp_params_infile="vdyp_params-landp",
        vdyp_io_dirname=str(tmp_path / "vdyp_io"),
        vdyp_log_path=tmp_path / "vdyp_io" / "vdyp_runs.jsonl",
        vdyp_stdout_log_path=tmp_path / "vdyp_io" / "vdyp_stdout.log",
        vdyp_stderr_log_path=tmp_path / "vdyp_io" / "vdyp_stderr.log",
        phase="initial",
        write_vdyp_infiles=lambda *_args: None,
        import_vdyp_tables_fn=lambda _path: (_ for _ in ()).throw(
            ValueError("bad parse")
        ),
        append_jsonl_fn=fake_append_jsonl,
        append_text_fn=lambda *_args: None,
        subprocess_run=lambda *_args, **_kwargs: _RunResult(stdout="", stderr=""),
    )

    assert out == {}
    assert len(events) == 1
    assert events[0]["status"] == "parse_error"


def test_execute_vdyp_batch_logs_timeout(tmp_path: Path) -> None:
    (tmp_path / "vdyp_io").mkdir(parents=True)
    vdyp_ply, vdyp_lyr = _sample_vdyp_tables()
    events: list[dict[str, object]] = []

    def fake_append_jsonl(_path: str | Path, payload: object) -> None:
        assert isinstance(payload, dict)
        events.append(payload)

    def timeout_run(*_args: object, **_kwargs: object) -> _RunResult:
        raise subprocess.TimeoutExpired(cmd="vdyp", timeout=5)

    out = execute_vdyp_batch(
        feature_ids=[1],
        vdyp_ply=vdyp_ply,
        vdyp_lyr=vdyp_lyr,
        vdyp_binpath="VDYP7/VDYP7/VDYP7Console.exe",
        vdyp_params_infile="vdyp_params-landp",
        vdyp_io_dirname=str(tmp_path / "vdyp_io"),
        vdyp_log_path=tmp_path / "vdyp_io" / "vdyp_runs.jsonl",
        vdyp_stdout_log_path=tmp_path / "vdyp_io" / "vdyp_stdout.log",
        vdyp_stderr_log_path=tmp_path / "vdyp_io" / "vdyp_stderr.log",
        phase="initial",
        write_vdyp_infiles=lambda *_args: None,
        import_vdyp_tables_fn=lambda _path: {},
        append_jsonl_fn=fake_append_jsonl,
        append_text_fn=lambda *_args: None,
        subprocess_run=timeout_run,
    )

    assert out == {}
    assert len(events) == 1
    assert events[0]["status"] == "timeout"


def test_execute_bootstrap_vdyp_runs_success() -> None:
    events: list[dict[str, object]] = []

    def append_event(_path: str | Path, payload: object) -> None:
        assert isinstance(payload, dict)
        events.append(payload)

    def fake_run_vdyp(sample: object, **_kwargs: object) -> dict[int, dict[str, str]]:
        assert sample == "sample-ss"
        return {1: {"curve": "ok"}}

    results = execute_bootstrap_vdyp_runs(
        tsa="08",
        run_id="run-1",
        results_for_tsa=[(3, "S1", {"L": {"ss": "sample-ss"}})],
        si_levels=["L"],
        vdyp_run_events_path="dummy.jsonl",
        append_jsonl_fn=append_event,
        run_vdyp_fn=fake_run_vdyp,
        verbose=False,
    )

    assert results == {3: {"L": {1: {"curve": "ok"}}}}
    assert len(events) == 1
    assert events[0]["status"] == "dispatch"
    assert events[0]["phase"] == "bootstrap"


def test_execute_bootstrap_vdyp_runs_logs_dispatch_error() -> None:
    events: list[dict[str, object]] = []

    def append_event(_path: str | Path, payload: object) -> None:
        assert isinstance(payload, dict)
        events.append(payload)

    def failing_run_vdyp(
        _sample: object, **_kwargs: object
    ) -> dict[int, dict[str, str]]:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        execute_bootstrap_vdyp_runs(
            tsa="08",
            run_id="run-1",
            results_for_tsa=[(5, "S2", {"L": {"ss": "sample-ss"}})],
            si_levels=["L"],
            vdyp_run_events_path="dummy.jsonl",
            append_jsonl_fn=append_event,
            run_vdyp_fn=failing_run_vdyp,
            verbose=False,
        )

    assert len(events) == 2
    assert events[0]["status"] == "dispatch"
    assert events[1]["status"] == "dispatch_error"


def test_execute_curve_smoothing_runs_builds_output_and_logs_missing() -> None:
    events: list[dict[str, object]] = []

    def append_event(_path: str | Path, payload: object) -> None:
        assert isinstance(payload, dict)
        events.append(payload)

    def fake_process(
        vdyp_out: object, **kwargs: object
    ) -> tuple[list[float], list[float]]:
        assert isinstance(vdyp_out, dict)
        assert kwargs["curve_context"]["stratum_code"] == "S1"
        assert kwargs["custom_knob"] == 7
        return [1.0, 20.0, 40.0], [1e-6, 120.0, 180.0]

    smoothed_runs = execute_curve_smoothing_runs(
        tsa="08",
        run_id="run-1",
        results_for_tsa=[
            (1, "S1", {}),
            (2, "S2", {}),
        ],
        si_levels=["L"],
        vdyp_results_for_tsa={
            1: {"L": {101: {"dummy": "ok"}}},
        },
        kwarg_overrides_for_tsa={("S1", "L"): {"custom_knob": 7}},
        process_vdyp_out_fn=fake_process,
        append_jsonl_fn=append_event,
        vdyp_curve_events_path="curve.jsonl",
        curve_fit_fn=lambda *_a, **_k: None,
        body_fit_func=lambda *_a, **_k: None,
        body_fit_func_bounds_func=lambda *_a, **_k: None,
        toe_fit_func=lambda *_a, **_k: None,
        toe_fit_func_bounds_func=lambda *_a, **_k: None,
        message_fn=lambda *_args, **_kwargs: None,
    )

    assert len(smoothed_runs) == 1
    assert smoothed_runs[0].stratum_code == "S1"
    assert smoothed_runs[0].si_level == "L"
    assert list(smoothed_runs[0].y) == [1e-6, 120.0, 180.0]
    assert len(events) == 1
    assert events[0]["status"] == "warning"
    assert events[0]["reason"] == "missing_vdyp_output"


def test_plot_curve_overlays_renders_expected_series() -> None:
    class _FakePlt:
        def __init__(self) -> None:
            self.plot_calls: list[tuple[object, object, dict[str, object]]] = []
            self.xlim_calls: list[tuple[float, float]] = []
            self.ylim_calls: list[tuple[float, float]] = []
            self.legend_calls = 0
            self.tight_layout_calls = 0

        def subplots(self, *_args: object, **_kwargs: object) -> tuple[None, None]:
            return None, None

        def plot(self, x: object, y: object, **kwargs: object) -> None:
            self.plot_calls.append((x, y, kwargs))

        def legend(self) -> None:
            self.legend_calls += 1

        def xlim(self, v: tuple[float, float]) -> None:
            self.xlim_calls.append(v)

        def ylim(self, v: tuple[float, float]) -> None:
            self.ylim_calls.append(v)

        def tight_layout(self) -> None:
            self.tight_layout_calls += 1

    fake_plt = _FakePlt()
    vdyp_df = pd.DataFrame(
        {"Vdwb": [100.0, 150.0]}, index=pd.Index([30, 60], name="Age")
    )
    smoothed_runs = [
        SmoothedCurveResult(
            stratumi=1,
            stratum_code="S1",
            si_level="L",
            x=[1.0, 40.0],
            y=[1e-6, 120.0],
            vdyp_out={101: vdyp_df},
        )
    ]
    plot_curve_overlays(
        results_for_tsa=[(1, "S1", {})],
        si_levels=["L"],
        smoothed_runs=smoothed_runs,
        plot=True,
        figsize=(8, 6),
        palette=["green"],
        pd_module=pd,
        plt_module=fake_plt,
        dataframe_type=pd.DataFrame,
        xlim=(0, 300),
        ylim=(0, 600),
        message_fn=lambda *_a, **_k: None,
    )

    assert len(fake_plt.plot_calls) == 2
    assert fake_plt.legend_calls == 1
    assert fake_plt.xlim_calls == [(0, 300)]
    assert fake_plt.ylim_calls == [(0, 600)]
    assert fake_plt.tight_layout_calls == 1


def test_build_smoothed_curve_table_builds_rows_and_writes_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    written_paths: list[Path] = []

    def fake_to_feather(self: pd.DataFrame, path: str | Path) -> None:
        written_paths.append(Path(path))

    monkeypatch.setattr(pd.DataFrame, "to_feather", fake_to_feather)
    runs = [
        SmoothedCurveResult(
            stratumi=1,
            stratum_code="S1",
            si_level="L",
            x=[1.0, 20.0, 40.0],
            y=[1e-6, 120.0, 180.0],
            vdyp_out={},
        ),
        SmoothedCurveResult(
            stratumi=2,
            stratum_code="S2",
            si_level="M",
            x=[1.0, 50.0],
            y=[1e-6, 210.0],
            vdyp_out={},
        ),
    ]
    output_path = tmp_path / "curves.feather"
    table = build_smoothed_curve_table(
        smoothed_runs=runs,
        pd_module=pd,
        output_path=output_path,
    )

    assert set(table["stratum_code"]) == {"S1", "S2"}
    assert set(table["si_level"]) == {"L", "M"}
    assert written_paths == [output_path]


def test_load_or_build_vdyp_results_tsa_force_run_builds_and_writes(
    tmp_path: Path,
) -> None:
    tsa_path = tmp_path / "vdyp_results-tsa08.pkl"
    combined_path = tmp_path / "vdyp_results.pkl"
    expected = {1: {"L": {101: {"ok": True}}}}

    out = load_or_build_vdyp_results_tsa(
        tsa="08",
        force_run_vdyp=True,
        vdyp_results_tsa_pickle_path=tsa_path,
        vdyp_results_pickle_path=combined_path,
        run_bootstrap_fn=lambda: expected,
        print_fn=lambda *_a, **_k: None,
    )

    assert out == expected
    assert tsa_path.exists()


def test_load_or_build_vdyp_results_tsa_reads_combined_cache_with_int_key(
    tmp_path: Path,
) -> None:
    tsa_path = tmp_path / "vdyp_results-tsa08.pkl"
    combined_path = tmp_path / "vdyp_results.pkl"
    with combined_path.open("wb") as handle:
        import pickle

        pickle.dump({8: {2: {"M": {202: {"ok": True}}}}}, handle)

    out = load_or_build_vdyp_results_tsa(
        tsa="08",
        force_run_vdyp=False,
        vdyp_results_tsa_pickle_path=tsa_path,
        vdyp_results_pickle_path=combined_path,
        run_bootstrap_fn=lambda: {},
        print_fn=lambda *_a, **_k: None,
    )

    assert out == {2: {"M": {202: {"ok": True}}}}


def test_load_or_build_vdyp_results_tsa_uses_tsa_cache_when_present(
    tmp_path: Path,
) -> None:
    tsa_path = tmp_path / "vdyp_results-tsa08.pkl"
    combined_path = tmp_path / "vdyp_results.pkl"
    expected = {9: {"H": {909: {"ok": True}}}}
    with tsa_path.open("wb") as handle:
        import pickle

        pickle.dump(expected, handle)

    out = load_or_build_vdyp_results_tsa(
        tsa="08",
        force_run_vdyp=False,
        vdyp_results_tsa_pickle_path=tsa_path,
        vdyp_results_pickle_path=combined_path,
        run_bootstrap_fn=lambda: {},
        print_fn=lambda *_a, **_k: None,
    )

    assert out == expected


def test_load_or_build_vdyp_results_tsa_compat_loader_fallback(tmp_path: Path) -> None:
    expected = {4: {"L": {404: {"ok": True}}}}
    combined_path = tmp_path / "combined.pkl"
    combined_path.write_bytes(b"placeholder")

    out = load_or_build_vdyp_results_tsa(
        tsa="08",
        force_run_vdyp=False,
        vdyp_results_tsa_pickle_path=tmp_path / "missing-tsa.pkl",
        vdyp_results_pickle_path=combined_path,
        run_bootstrap_fn=lambda: {},
        print_fn=lambda *_a, **_k: None,
        load_pickle_fn=lambda _path: (_ for _ in ()).throw(
            ModuleNotFoundError("legacy")
        ),
        load_compat_pickle_fn=lambda _path: {"08": expected},
        dump_pickle_fn=lambda _v, _p: None,
    )

    assert out == expected


def test_load_vdyp_input_tables_reads_feather_by_default() -> None:
    class _FakeTable:
        def __init__(self, name: str) -> None:
            self.name = name
            self.writes: list[Path] = []

        def to_feather(self, path: str | Path) -> None:
            self.writes.append(Path(path))

    class _FakeGpd:
        def __init__(self) -> None:
            self.read_file_calls: list[tuple[object, object, object]] = []
            self.read_feather_calls: list[object] = []

        def read_file(self, path: object, driver: object, layer: object) -> _FakeTable:
            self.read_file_calls.append((path, driver, layer))
            return _FakeTable(f"file-{layer}")

        def read_feather(self, path: object) -> _FakeTable:
            self.read_feather_calls.append(path)
            return _FakeTable(f"feather-{path}")

    fake_gpd = _FakeGpd()
    ply, lyr = load_vdyp_input_tables(
        vdyp_input_pandl_path="input.gdb",
        vdyp_ply_feather_path="ply.feather",
        vdyp_lyr_feather_path="lyr.feather",
        read_from_source=False,
        gpd_module=fake_gpd,
    )

    assert ply.name == "feather-ply.feather"
    assert lyr.name == "feather-lyr.feather"
    assert fake_gpd.read_feather_calls == ["ply.feather", "lyr.feather"]
    assert fake_gpd.read_file_calls == []


def test_load_vdyp_input_tables_reads_source_and_writes_feather() -> None:
    class _FakeTable:
        def __init__(self, name: str) -> None:
            self.name = name
            self.writes: list[Path] = []

        def to_feather(self, path: str | Path) -> None:
            self.writes.append(Path(path))

    class _FakeGpd:
        def __init__(self) -> None:
            self.tables: dict[int, _FakeTable] = {}
            self.read_file_calls: list[tuple[object, object, object]] = []
            self.read_feather_calls: list[object] = []

        def read_file(self, path: object, driver: object, layer: int) -> _FakeTable:
            self.read_file_calls.append((path, driver, layer))
            table = _FakeTable(f"file-{layer}")
            self.tables[layer] = table
            return table

        def read_feather(self, path: object) -> _FakeTable:
            self.read_feather_calls.append(path)
            return _FakeTable(f"feather-{path}")

    fake_gpd = _FakeGpd()
    ply, lyr = load_vdyp_input_tables(
        vdyp_input_pandl_path="input.gdb",
        vdyp_ply_feather_path="ply.feather",
        vdyp_lyr_feather_path="lyr.feather",
        read_from_source=True,
        gpd_module=fake_gpd,
    )

    assert ply.name == "file-0"
    assert lyr.name == "file-1"
    assert fake_gpd.read_file_calls == [
        ("input.gdb", "FileGDB", 0),
        ("input.gdb", "FileGDB", 1),
    ]
    assert fake_gpd.read_feather_calls == []
    assert fake_gpd.tables[0].writes == [Path("ply.feather")]
    assert fake_gpd.tables[1].writes == [Path("lyr.feather")]

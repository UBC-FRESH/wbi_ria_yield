"""Reusable pipeline helpers for legacy workflow migration."""

from __future__ import annotations

from femic.pipeline.io import (
    DEFAULT_DEV_CONFIG_PATH,
    FALLBACK_DEFAULT_TSA_LIST,
    LegacyExecutionPlan,
    PipelineRunConfig,
    build_legacy_execution_plan,
    build_pipeline_run_config,
    load_default_tsa_list,
    normalize_tsa_list,
)
from femic.pipeline.manifest import (
    build_run_manifest_payload,
    collect_runtime_versions,
    write_manifest,
)
from femic.pipeline.pre_vdyp import (
    load_vdyp_prep_checkpoint,
    save_vdyp_prep_checkpoint,
    serialize_vdyp_prep_payload,
)
from femic.pipeline.vdyp_logging import (
    append_jsonl,
    append_text,
    build_tsa_vdyp_log_paths,
    resolve_run_id,
    vdyp_log_base,
)
from femic.pipeline.vdyp_curves import (
    fill_curve_left,
    prepend_quasi_origin_point,
    process_vdyp_out,
)
from femic.pipeline.stages import StageResult, run_legacy_subprocess
from femic.pipeline.vdyp_sampling import nsamples_from_curves
from femic.pipeline.vdyp_io import import_vdyp_tables, write_vdyp_infiles_plylyr
from femic.pipeline.tipsy import compute_vdyp_oaf1, compute_vdyp_site_index
from femic.pipeline.vdyp import build_vdyp_log_paths

__all__ = [
    "DEFAULT_DEV_CONFIG_PATH",
    "FALLBACK_DEFAULT_TSA_LIST",
    "LegacyExecutionPlan",
    "PipelineRunConfig",
    "StageResult",
    "build_legacy_execution_plan",
    "run_legacy_subprocess",
    "build_run_manifest_payload",
    "collect_runtime_versions",
    "load_vdyp_prep_checkpoint",
    "save_vdyp_prep_checkpoint",
    "serialize_vdyp_prep_payload",
    "append_jsonl",
    "append_text",
    "build_tsa_vdyp_log_paths",
    "resolve_run_id",
    "vdyp_log_base",
    "fill_curve_left",
    "prepend_quasi_origin_point",
    "process_vdyp_out",
    "import_vdyp_tables",
    "write_vdyp_infiles_plylyr",
    "nsamples_from_curves",
    "compute_vdyp_oaf1",
    "compute_vdyp_site_index",
    "write_manifest",
    "build_vdyp_log_paths",
    "build_pipeline_run_config",
    "load_default_tsa_list",
    "normalize_tsa_list",
]

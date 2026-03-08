"""Shared FMG core model dataclasses used by export adapters/writers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CurvePoint:
    """One curve point."""

    x: float
    y: float


@dataclass(frozen=True)
class CurveDefinition:
    """Curve payload with type and ordered points."""

    curve_id: int
    curve_type: str
    points: tuple[CurvePoint, ...]


@dataclass(frozen=True)
class AnalysisUnitDefinition:
    """Normalized AU row required for downstream exports."""

    au_id: int
    tsa: str
    stratum_code: str
    si_level: str
    managed_curve_id: int
    unmanaged_curve_id: int


@dataclass(frozen=True)
class BundleModelContext:
    """Shared parsed context from FEMIC bundle tables."""

    tsa_list: list[str]
    analysis_units: tuple[AnalysisUnitDefinition, ...]
    curves_by_id: dict[int, CurveDefinition]
    managed_species_curve_ids: dict[int, dict[str, int]]
    unmanaged_species_curve_ids: dict[int, dict[str, int]]
    curve_row_count: int

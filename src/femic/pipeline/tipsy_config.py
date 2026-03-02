"""Config-driven TIPSY rule loading and evaluation helpers."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import re
from typing import Any, Mapping

import yaml

from femic.pipeline.tipsy import compute_vdyp_oaf1, compute_vdyp_site_index

TipsyParamBuilder = Callable[
    [int, Mapping[str, Any], Mapping[Any, Any]], dict[str, dict[str, Any]]
]


def tipsy_config_path_for_tsa(tsa_code: str, config_dir: str | Path) -> Path:
    """Resolve default config path (`tsaXX.yaml`) for a TSA code."""
    tsa = str(tsa_code).zfill(2)
    return Path(config_dir) / f"tsa{tsa}.yaml"


def _resolve_tipsy_config_path(
    *,
    tsa_code: str,
    config_dir: str | Path,
) -> Path | None:
    path_yaml = tipsy_config_path_for_tsa(tsa_code, config_dir)
    path_yml = path_yaml.with_suffix(".yml")
    if path_yaml.exists():
        return path_yaml
    if path_yml.exists():
        return path_yml
    return None


def load_tipsy_tsa_config(
    *,
    tsa_code: str,
    config_dir: str | Path = "config/tipsy",
) -> dict[str, Any] | None:
    """Load and validate TSA config; return `None` if no TSA config file exists."""
    path = _resolve_tipsy_config_path(tsa_code=tsa_code, config_dir=config_dir)
    if path is None:
        return None
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"TIPSY config is not a mapping: {path}")
    validate_tipsy_tsa_config(payload, tsa_code=tsa_code, path=path)
    return payload


def resolve_tipsy_param_builder(
    *,
    tsa_code: str,
    legacy_builder: TipsyParamBuilder,
    config_dir: str | Path = "config/tipsy",
    use_legacy: bool = False,
) -> tuple[TipsyParamBuilder, str]:
    """Resolve active TIPSY param builder (config-driven or legacy) for a TSA."""
    tsa = str(tsa_code).zfill(2)
    cfg = load_tipsy_tsa_config(tsa_code=tsa, config_dir=config_dir)
    if cfg is not None and not use_legacy:
        cfg_path = _resolve_tipsy_config_path(tsa_code=tsa, config_dir=config_dir)
        assert cfg_path is not None

        def _tipsy_params_from_config(
            au_id: int,
            au_data: Mapping[str, Any],
            vdyp_out: Mapping[Any, Any],
        ) -> dict[str, dict[str, Any]]:
            return build_tipsy_params_from_config(
                au_id=au_id,
                au_data=au_data,
                vdyp_out=vdyp_out,
                config=cfg,
            )

        return (
            _tipsy_params_from_config,
            f"using config-driven TIPSY rules from {cfg_path}",
        )
    if use_legacy:
        return (
            legacy_builder,
            "using legacy in-code TIPSY rules (FEMIC_TIPSY_USE_LEGACY=1)",
        )
    raise RuntimeError(
        f"Missing TIPSY config for TSA {tsa} in {config_dir}. "
        "Provide config/tipsy/tsaXX.yaml or set FEMIC_TIPSY_USE_LEGACY=1."
    )


def discover_tipsy_config_tsas(
    config_dir: str | Path = "config/tipsy",
) -> dict[str, Path]:
    """Discover TSA config files under a directory."""
    base = Path(config_dir)
    found: dict[str, Path] = {}
    if not base.exists():
        return found
    for path in sorted(base.glob("tsa*.y*ml")):
        match = re.fullmatch(r"tsa(\d+)\.ya?ml", path.name)
        if not match:
            continue
        found[match.group(1).zfill(2)] = path
    return found


def validate_tipsy_tsa_config(
    payload: Mapping[str, Any],
    *,
    tsa_code: str,
    path: Path,
) -> None:
    """Perform lightweight structural validation for config-driven rules."""
    schema_version = payload.get("schema_version")
    if schema_version != 1:
        raise ValueError(
            f"Unsupported TIPSY schema_version in {path}: {schema_version!r}"
        )
    tsa_value = str(payload.get("tsa_code", "")).zfill(2)
    if tsa_value != str(tsa_code).zfill(2):
        raise ValueError(
            f"TIPSY config TSA mismatch in {path}: expected {str(tsa_code).zfill(2)!r}, "
            f"found {tsa_value!r}"
        )
    rules = payload.get("rules")
    if not isinstance(rules, list) or not rules:
        raise ValueError(f"TIPSY config {path} must include non-empty 'rules'")
    for idx, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise ValueError(f"TIPSY config {path} rule[{idx}] must be a mapping")
        if not isinstance(rule.get("id"), str) or not rule["id"].strip():
            raise ValueError(f"TIPSY config {path} rule[{idx}] missing non-empty 'id'")
        when = rule.get("when")
        if not isinstance(when, dict):
            raise ValueError(f"TIPSY config {path} rule[{idx}] missing mapping 'when'")
        assign = rule.get("assign")
        if not isinstance(assign, dict):
            raise ValueError(
                f"TIPSY config {path} rule[{idx}] missing mapping 'assign'"
            )
        for side in ("e", "f"):
            if not isinstance(assign.get(side), dict):
                raise ValueError(
                    f"TIPSY config {path} rule[{idx}] assign.{side} must be a mapping"
                )


def _rule_matches(
    rule: Mapping[str, Any],
    *,
    leading_species: str,
    bec: str,
    forest_type: int | None,
) -> bool:
    when = rule.get("when", {})
    if not isinstance(when, Mapping):
        return False
    species_allow = when.get("leading_species_in")
    if isinstance(species_allow, list) and leading_species not in species_allow:
        return False
    bec_allow = when.get("bec_in")
    if isinstance(bec_allow, list) and bec not in bec_allow:
        return False
    forest_allow = when.get("forest_type_in")
    if isinstance(forest_allow, list) and forest_type not in forest_allow:
        return False
    return True


def _normalize_species_for_tipsy(species: str) -> str:
    """Normalize species codes for TIPSY compatibility where needed."""
    return "SW" if species == "SX" else species


def _resolve_assignment_value(
    value: Any,
    *,
    leading_species: str,
    bec: str,
    forest_type: int | None,
    species_ranked: list[tuple[str, float]],
) -> Any:
    if not isinstance(value, str):
        return value
    if value == "$leading_species":
        return leading_species
    if value == "$leading_species_tipsy":
        return _normalize_species_for_tipsy(leading_species)
    if value == "$bec":
        return bec
    if value == "$forest_type":
        return forest_type
    match_spp = re.fullmatch(r"\$species_rank_(\d+)_tipsy", value)
    if match_spp:
        idx = int(match_spp.group(1)) - 1
        if 0 <= idx < len(species_ranked):
            return _normalize_species_for_tipsy(species_ranked[idx][0])
        return None
    match_pct = re.fullmatch(r"\$species_pct_(\d+)", value)
    if match_pct:
        idx = int(match_pct.group(1)) - 1
        if 0 <= idx < len(species_ranked):
            return species_ranked[idx][1]
        return None
    return value


def _resolve_assignment_block(
    block: Mapping[str, Any],
    *,
    leading_species: str,
    bec: str,
    forest_type: int | None,
    species_ranked: list[tuple[str, float]],
) -> dict[str, Any]:
    return {
        key: _resolve_assignment_value(
            value,
            leading_species=leading_species,
            bec=bec,
            forest_type=forest_type,
            species_ranked=species_ranked,
        )
        for key, value in block.items()
    }


def build_tipsy_params_from_config(
    *,
    au_id: int,
    au_data: Mapping[str, Any],
    vdyp_out: Mapping[Any, Any],
    config: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    """Build TIPSY parameter rows using configured rule assignments."""
    tp: dict[str, dict[str, Any]] = {"e": {}, "f": {}}
    ss = au_data["ss"]
    species = au_data["species"]
    leading_species = list(species.keys())[0]
    species_ranked = [
        (str(spp), float(species[spp]["pct"]))
        for spp in species
        if isinstance(species[spp], Mapping) and "pct" in species[spp]
    ]
    bec = ss.BEC_ZONE_CODE.iloc[0]
    forest_type: int | None = None
    if "forest_type" in ss:
        try:
            forest_type = int(ss["forest_type"].mode().iloc[0])
        except Exception:
            forest_type = None

    for side in ("e", "f"):
        defaults = config.get("defaults", {}).get(side, {})
        if isinstance(defaults, Mapping):
            tp[side].update(
                _resolve_assignment_block(
                    defaults,
                    leading_species=leading_species,
                    bec=bec,
                    forest_type=forest_type,
                    species_ranked=species_ranked,
                )
            )
    for rule in config["rules"]:
        if _rule_matches(
            rule,
            leading_species=leading_species,
            bec=bec,
            forest_type=forest_type,
        ):
            for side in ("e", "f"):
                tp[side].update(
                    _resolve_assignment_block(
                        rule["assign"][side],
                        leading_species=leading_species,
                        bec=bec,
                        forest_type=forest_type,
                        species_ranked=species_ranked,
                    )
                )
            break
    else:
        raise ValueError(
            f"No TIPSY config rule matched AU {au_id} (leading_species={leading_species}, "
            f"BEC={bec}, forest_type={forest_type})"
        )

    si = compute_vdyp_site_index(vdyp_out)
    if si != si:  # NaN
        si = round(float(ss.SITE_INDEX.median()), 1)
    oaf1 = compute_vdyp_oaf1(vdyp_out)
    if oaf1 != oaf1:  # NaN
        oaf1 = 0.85

    tp["e"]["AU"] = tp["e"]["TBLno"] = 10000 + int(au_id)
    tp["f"]["AU"] = tp["f"]["TBLno"] = 20000 + int(au_id)
    tp["e"]["SI"] = tp["f"]["SI"] = si
    tp["e"]["BEC"] = tp["f"]["BEC"] = bec
    tp["e"]["OAF1"] = tp["f"]["OAF1"] = oaf1
    return tp

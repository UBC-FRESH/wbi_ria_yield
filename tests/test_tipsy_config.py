from __future__ import annotations

from pathlib import Path

import pandas as pd

from femic.pipeline.tipsy_config import (
    build_tipsy_params_from_config,
    load_tipsy_tsa_config,
)


def test_load_tipsy_tsa_config_returns_none_when_missing(tmp_path: Path) -> None:
    assert load_tipsy_tsa_config(tsa_code="08", config_dir=tmp_path) is None


def test_load_tipsy_tsa_config_parses_and_validates(tmp_path: Path) -> None:
    path = tmp_path / "tsa08.yaml"
    path.write_text(
        """
schema_version: 1
tsa_code: "08"
rules:
  - id: spruce
    when:
      leading_species_in: ["SW"]
      bec_in: ["SBS"]
    assign:
      e: {Density: 1200, SPP_1: "SW", PCT_1: 100}
      f: {Density: 1100, SPP_1: "SW", PCT_1: 100}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    payload = load_tipsy_tsa_config(tsa_code="08", config_dir=tmp_path)
    assert payload is not None
    assert payload["tsa_code"] == "08"


def test_build_tipsy_params_from_config_assigns_rule_and_derived_fields() -> None:
    cfg = {
        "schema_version": 1,
        "tsa_code": "08",
        "defaults": {
            "e": {"Proportion": 1, "Regen_Method": "P"},
            "f": {"Proportion": 1, "Regen_Method": "P"},
        },
        "rules": [
            {
                "id": "spruce_rule",
                "when": {"leading_species_in": ["SW"], "bec_in": ["SBS"]},
                "assign": {
                    "e": {"Density": 1200, "SPP_1": "SW", "PCT_1": 100},
                    "f": {"Density": 1100, "SPP_1": "SW", "PCT_1": 100},
                },
            }
        ],
    }
    au_data = {
        "ss": pd.DataFrame(
            {"SITE_INDEX": [16.0, 18.0], "BEC_ZONE_CODE": ["SBS", "SBS"]},
        ),
        "species": {"SW": {"pct": 60.0}},
    }
    vdyp_out = {
        1: pd.DataFrame({"SI": [17.0, 18.0], "% Stk": [85.0, 85.0]}),
        2: pd.DataFrame({"SI": [16.0, 17.0], "% Stk": [95.0, 95.0]}),
    }
    out = build_tipsy_params_from_config(
        au_id=3001,
        au_data=au_data,
        vdyp_out=vdyp_out,
        config=cfg,
    )
    assert out["e"]["TBLno"] == 13001
    assert out["f"]["TBLno"] == 23001
    assert out["e"]["BEC"] == "SBS"
    assert out["e"]["SPP_1"] == "SW"
    assert out["f"]["Density"] == 1100


def test_build_tipsy_params_from_config_resolves_species_token_for_sx() -> None:
    cfg = {
        "schema_version": 1,
        "tsa_code": "08",
        "defaults": {
            "e": {"SPP_1": "$leading_species_tipsy"},
            "f": {"SPP_1": "$leading_species_tipsy"},
        },
        "rules": [
            {
                "id": "spruce_rule",
                "when": {"leading_species_in": ["SX"]},
                "assign": {"e": {"Density": 1000}, "f": {"Density": 900}},
            }
        ],
    }
    au_data = {
        "ss": pd.DataFrame({"SITE_INDEX": [15.0], "BEC_ZONE_CODE": ["SBS"]}),
        "species": {"SX": {"pct": 70.0}},
    }
    vdyp_out = {1: pd.DataFrame({"SI": [15.0], "% Stk": [90.0]})}
    out = build_tipsy_params_from_config(
        au_id=3002,
        au_data=au_data,
        vdyp_out=vdyp_out,
        config=cfg,
    )
    assert out["e"]["SPP_1"] == "SW"
    assert out["f"]["SPP_1"] == "SW"


def test_repo_tsa16_config_loads_and_matches_spruce_rule() -> None:
    cfg = load_tipsy_tsa_config(tsa_code="16", config_dir="config/tipsy")
    assert cfg is not None
    au_data = {
        "ss": pd.DataFrame({"SITE_INDEX": [18.0], "BEC_ZONE_CODE": ["SBS"]}),
        "species": {"SW": {"pct": 55.0}},
    }
    vdyp_out = {1: pd.DataFrame({"SI": [18.0], "% Stk": [90.0]})}
    out = build_tipsy_params_from_config(
        au_id=4001,
        au_data=au_data,
        vdyp_out=vdyp_out,
        config=cfg,
    )
    assert out["e"]["Density"] == 1147
    assert out["f"]["Density"] == 1245
    assert out["e"]["SPP_1"] == "SW"
    assert out["f"]["SPP_2"] == "PLI"


def test_repo_tsa24_config_loads_and_matches_sbs_pine_rule() -> None:
    cfg = load_tipsy_tsa_config(tsa_code="24", config_dir="config/tipsy")
    assert cfg is not None
    au_data = {
        "ss": pd.DataFrame({"SITE_INDEX": [16.0], "BEC_ZONE_CODE": ["SBS"]}),
        "species": {"PL": {"pct": 70.0}},
    }
    vdyp_out = {1: pd.DataFrame({"SI": [16.0], "% Stk": [88.0]})}
    out = build_tipsy_params_from_config(
        au_id=5001,
        au_data=au_data,
        vdyp_out=vdyp_out,
        config=cfg,
    )
    assert out["e"]["Density"] == 5700
    assert out["f"]["Density"] == 1700
    assert out["e"]["Regen_Method"] == "N"
    assert out["f"]["SPP_1"] == "PL"


def test_repo_tsa24_config_loads_and_matches_essf_spruce_rule() -> None:
    cfg = load_tipsy_tsa_config(tsa_code="24", config_dir="config/tipsy")
    assert cfg is not None
    au_data = {
        "ss": pd.DataFrame({"SITE_INDEX": [15.0], "BEC_ZONE_CODE": ["ESSF"]}),
        "species": {"SW": {"pct": 60.0}},
    }
    vdyp_out = {1: pd.DataFrame({"SI": [15.0], "% Stk": [92.0]})}
    out = build_tipsy_params_from_config(
        au_id=5002,
        au_data=au_data,
        vdyp_out=vdyp_out,
        config=cfg,
    )
    assert out["e"]["Density"] == 1500
    assert out["e"]["SPP_1"] == "SE"
    assert out["f"]["GW_1"] == 18


def test_repo_tsa40_config_uses_ranked_species_tokens() -> None:
    cfg = load_tipsy_tsa_config(tsa_code="40", config_dir="config/tipsy")
    assert cfg is not None
    au_data = {
        "ss": pd.DataFrame({"SITE_INDEX": [17.0], "BEC_ZONE_CODE": ["BWBS"]}),
        "species": {"SX": {"pct": 60.0}, "AT": {"pct": 30.0}},
    }
    vdyp_out = {1: pd.DataFrame({"SI": [17.0], "% Stk": [89.0]})}
    out = build_tipsy_params_from_config(
        au_id=6001,
        au_data=au_data,
        vdyp_out=vdyp_out,
        config=cfg,
    )
    assert out["e"]["SPP_1"] == "SW"
    assert out["e"]["PCT_1"] == 60.0
    assert out["e"]["SPP_2"] == "AT"
    assert out["e"]["PCT_2"] == 30.0
    assert out["f"]["Density"] == 1167


def test_repo_tsa41_config_matches_forest_type_rule() -> None:
    cfg = load_tipsy_tsa_config(tsa_code="41", config_dir="config/tipsy")
    assert cfg is not None
    au_data = {
        "ss": pd.DataFrame(
            {"SITE_INDEX": [16.0], "BEC_ZONE_CODE": ["BWBS"], "forest_type": [1]}
        ),
        "species": {"PL": {"pct": 65.0}},
    }
    vdyp_out = {1: pd.DataFrame({"SI": [16.0], "% Stk": [93.0]})}
    out = build_tipsy_params_from_config(
        au_id=6002,
        au_data=au_data,
        vdyp_out=vdyp_out,
        config=cfg,
    )
    assert out["e"]["SPP_1"] == "PL"
    assert out["f"]["PCT_2"] == 27
    assert out["e"]["Density"] == 1219


def test_repo_all_legacy_tsa_configs_present() -> None:
    for tsa in ("08", "16", "24", "40", "41"):
        payload = load_tipsy_tsa_config(tsa_code=tsa, config_dir="config/tipsy")
        assert payload is not None

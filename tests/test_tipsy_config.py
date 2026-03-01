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

"""Legacy in-code TIPSY rule builders extracted from 01a workflow."""

from __future__ import annotations

import itertools

from femic.pipeline.tipsy import compute_vdyp_oaf1, compute_vdyp_site_index

species_spruce = ["S", "SB", "SE", "SN", "SS", "SW", "SX", "SXE", "SXL", "SXW"]
species_pine = ["P", "PA", "PJ", "PL", "PLC", "PLI", "PM"]
species_fir = ["B", "BA", "BB", "BG", "BL", "BM", "BP"]
species_larch = ["L", "LA", "LS", "LT", "LW"]
species_cedar = ["C", "CW"]
species_hemlock = ["HM", "HWI", "HW"]
species_douglasfir = ["F", "FD", "FDC", "FDI"]

species_aspen = ["AC", "ACB", "ACT", "AD", "AT", "AX"]
species_birch = ["E", "EA", "EB", "EE", "EP", "EW", "EXP"]
species_willow = ["W", "WA", "WB", "WD", "WP", "WS"]
species_alder = ["D", "DR"]
species_cherry = ["V"]
species_dogwood = ["GP"]
species_oak = ["Q"]
species_maple = ["M", "MB", "MV"]


# --- cell 50 ---
def tipsy_minsi_tsa08(leading_species):
    if leading_species in species_pine:
        return 15.0
    elif leading_species in species_aspen:
        return 15.0
    else:
        return 10.0


# --- cell 52 ---
tipsy_exclusion = {
    "08": {
        "min_si": tipsy_minsi_tsa08,
        "min_vol": lambda s: 140.0,
        "excl_bec": [],
        "excl_leading_species": list(
            itertools.chain(
                species_aspen,
                species_birch,
                species_larch,
                species_willow,
                species_alder,
                species_cherry,
                species_dogwood,
                species_oak,
                ["SB"],
            )
        ),
    },
    "16": {
        "min_si": lambda s: 5.0,
        "min_vol": lambda s: 151.0,
        "excl_bec": [],
        "excl_leading_species": list(
            itertools.chain(species_willow, species_birch, species_larch)
        ),
    },
    "24": {
        "min_si": lambda s: 5.0,
        "min_vol": lambda s: 140.0 if s in species_pine else 182.0,
        "excl_bec": ["ICH"],
        "excl_leading_species": list(
            itertools.chain(species_hemlock, species_aspen, species_hemlock, ["SB"])
        ),
    },  # plus "non-commercial deciduous"... whatever that means (no definition of commercial species in TSR data package)
    "40": {
        "min_si": lambda s: 5.0,
        "min_vol": lambda s: 140.0,
        "excl_bec": [],
        "excl_leading_species": list(
            itertools.chain(species_birch, species_larch, ["SB", "ACT"])
        ),
    },
    "41": {
        "min_si": lambda s: 5.0,
        "min_vol": lambda s: 120.0,
        "excl_bec": [],
        "excl_leading_species": list(
            itertools.chain(
                species_cedar,
                species_hemlock,
                species_larch,
                species_fir,
                species_alder,
                species_maple,
                species_birch,
                ["SB"],
            )
        ),
    },
}


# --- cell 54 ---
def tipsy_params_tsa08(au_id, au_data, vdyp_out):
    tp = {"e": {}, "f": {}}
    # spp_pct = {spp:data['pct'] for spp, data in au_data['species'].items()}
    # spp_1 = list(spp_pct.keys())[0]
    spp_1 = list(au_data["species"].keys())[0]
    if spp_1 in species_spruce:
        if spp_1 == "SX":
            spp_1 = "SW"  # no SX in TIPSY
        tp["e"]["Density"] = 1472
        tp["f"]["Density"] = 1416
        tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 17.5
    elif spp_1 in species_pine:
        tp["e"]["Density"] = 1624
        tp["f"]["Density"] = 1285
        tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 12.5
    else:
        assert False  # only planting spruce and pine
    # si = au_data['ss'].siteprod.median()
    si = round(au_data["ss"].SITE_INDEX.median(), 1)
    # cc = au_data['ss'].CROWN_CLOSURE.median() * 0.01
    bec = au_data["ss"].BEC_ZONE_CODE.iloc[0]
    oaf1 = compute_vdyp_oaf1(vdyp_out)
    # tp['e']['AU'] = tp['f']['AU'] = au_id
    tp["e"]["AU"] = tp["e"]["TBLno"] = 10000 + au_id
    tp["f"]["AU"] = tp["f"]["TBLno"] = 20000 + au_id
    tp["e"]["BEC"] = tp["f"]["BEC"] = bec
    tp["e"]["Proportion"] = tp["f"]["Proportion"] = 1
    tp["e"]["Regen_Delay"] = 2
    tp["f"]["Regen_Delay"] = 1
    tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
    tp["e"]["OAF1"] = tp["f"]["OAF1"] = au_data["ss"] = (
        oaf1  # round(0.85 + (0.15 * cc), 2)
    )
    tp["e"]["OAF2"] = tp["f"]["OAF2"] = 0.95
    tp["e"]["FIZ"] = tp["f"]["FIZ"] = "I"
    tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = spp_1
    tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 100
    tp["e"]["SI"] = tp["f"]["SI"] = si
    tp["e"]["GW_1"] = tp["f"]["GW_1"] = None
    tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = None
    for i in range(2, 6):
        tp["e"]["SPP_%i" % i] = tp["f"]["SPP_%i" % i] = None
        tp["e"]["PCT_%i" % i] = tp["f"]["PCT_%i" % i] = None
        tp["e"]["GW_%i" % i] = tp["f"]["GW_%i" % i] = None
        tp["e"]["GW_age_%i" % i] = tp["f"]["GW_age_%i" % i] = None
    return tp


def tipsy_params_tsa16(au_id, au_data, vdyp_out):
    tp = {"e": {}, "f": {}}
    spp_1 = list(au_data["species"].keys())[0]
    if spp_1 in species_aspen:
        tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
        tp["e"]["Density"], tp["f"]["Density"] = 1317, 1405
        tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "AT"
        tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "PLI"
        tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "SW"
        tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = "BL"
        tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
        tp["e"]["PCT_1"], tp["f"]["PCT_1"] = 45, 49
        tp["e"]["PCT_2"], tp["f"]["PCT_2"] = 33, 33
        tp["e"]["PCT_3"], tp["f"]["PCT_3"] = 19, 14
        tp["e"]["PCT_4"], tp["f"]["PCT_4"] = 4, 4
        tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
        tp["e"]["GW_1"] = tp["f"]["GW_1"] = None
        tp["e"]["GW_2"], tp["f"]["GW_2"] = None, 2
        tp["e"]["GW_3"], tp["f"]["GW_3"] = None, 1
        tp["e"]["GW_4"] = tp["f"]["GW_4"] = None
        tp["e"]["GW_5"] = tp["f"]["GW_5"] = None
        tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = None
        tp["e"]["GW_age_2"], tp["f"]["GW_age_2"] = (
            None,
            12,
        )  # not specified in TSR data package (12 is "default" says Cosmin Man)
        tp["e"]["GW_age_3"], tp["f"]["GW_age_3"] = (
            None,
            12,
        )  # not specified in TSR data package (12 is "default" says Cosmin Man)
        tp["e"]["GW_age_4"] = tp["f"]["GW_age_4"] = None
        tp["e"]["GW_age_5"] = tp["f"]["GW_age_5"] = None
        tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 17.5
    elif spp_1 in species_fir:
        tp["e"]["Regen_Delay"], tp["f"]["Regen_Delay"] = 2, 1
        tp["e"]["Density"], tp["f"]["Density"] = 1126, 1216
        tp["e"]["SPP_1"], tp["f"]["SPP_1"] = "BL", "SW"
        tp["e"]["SPP_2"], tp["f"]["SPP_2"] = "SW", "PLI"
        tp["e"]["SPP_3"], tp["f"]["SPP_3"] = "PLI", "BL"
        tp["e"]["SPP_4"], tp["f"]["SPP_4"] = "AT", "AT"
        tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
        tp["e"]["PCT_1"], tp["f"]["PCT_1"] = 53, 50
        tp["e"]["PCT_2"], tp["f"]["PCT_2"] = 24, 27
        tp["e"]["PCT_3"], tp["f"]["PCT_3"] = 17, 21
        tp["e"]["PCT_4"], tp["f"]["PCT_4"] = 6, 2
        tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
        tp["e"]["GW_1"], tp["f"]["GW_1"] = None, 4
        tp["e"]["GW_2"] = tp["f"]["GW_2"] = None
        tp["e"]["GW_3"] = tp["f"]["GW_3"] = None
        tp["e"]["GW_4"] = tp["f"]["GW_4"] = None
        tp["e"]["GW_5"] = tp["f"]["GW_5"] = None
        tp["e"]["GW_age_1"], tp["f"]["GW_age_1"] = (
            None,
            12,
        )  # not specified in TSR data package (12 is "default" says Cosmin Man)
        tp["e"]["GW_age_2"] = tp["f"]["GW_age_2"] = None
        tp["e"]["GW_age_3"] = tp["f"]["GW_age_3"] = None
        tp["e"]["GW_age_4"] = tp["f"]["GW_age_4"] = None
        tp["e"]["GW_age_5"] = tp["f"]["GW_age_5"] = None
        tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 17.5
    elif spp_1 in species_pine:
        tp["e"]["Regen_Delay"], tp["f"]["Regen_Delay"] = 2, 1
        tp["e"]["Density"], tp["f"]["Density"] = 1196, 1231
        tp["e"]["SPP_1"], tp["f"]["SPP_1"] = "PLI", "PLI"
        tp["e"]["SPP_2"], tp["f"]["SPP_2"] = None, None
        tp["e"]["SPP_3"], tp["f"]["SPP_3"] = None, None
        tp["e"]["SPP_4"], tp["f"]["SPP_4"] = None, None
        tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
        tp["e"]["PCT_1"], tp["f"]["PCT_1"] = 100, 100
        tp["e"]["PCT_2"], tp["f"]["PCT_2"] = None, None
        tp["e"]["PCT_3"], tp["f"]["PCT_3"] = None, None
        tp["e"]["PCT_4"], tp["f"]["PCT_4"] = None, None
        tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
        tp["e"]["GW_1"] = tp["f"]["GW_1"] = None
        tp["e"]["GW_2"], tp["f"]["GW_2"] = None, None
        tp["e"]["GW_3"] = tp["f"]["GW_3"] = None
        tp["e"]["GW_4"] = tp["f"]["GW_4"] = None
        tp["e"]["GW_5"] = tp["f"]["GW_5"] = None
        tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = None
        tp["e"]["GW_age_2"], tp["f"]["GW_age_2"] = None, None
        tp["e"]["GW_age_3"] = tp["f"]["GW_age_3"] = None
        tp["e"]["GW_age_4"] = tp["f"]["GW_age_4"] = None
        tp["e"]["GW_age_5"] = tp["f"]["GW_age_5"] = None
        tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 12.5
    elif spp_1 in species_spruce:
        tp["e"]["Regen_Delay"], tp["f"]["Regen_Delay"] = 2, 1
        tp["e"]["Density"], tp["f"]["Density"] = 1147, 1245
        tp["e"]["SPP_1"], tp["f"]["SPP_1"] = "SW", "SW"
        tp["e"]["SPP_2"], tp["f"]["SPP_2"] = "BL", "PLI"
        tp["e"]["SPP_3"], tp["f"]["SPP_3"] = "PLI", "AT"
        tp["e"]["SPP_4"], tp["f"]["SPP_4"] = "AT", "BL"
        tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
        tp["e"]["PCT_1"], tp["f"]["PCT_1"] = 51, 43
        tp["e"]["PCT_2"], tp["f"]["PCT_2"] = 19, 38
        tp["e"]["PCT_3"], tp["f"]["PCT_3"] = 15, 12
        tp["e"]["PCT_4"], tp["f"]["PCT_4"] = 15, 8
        tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
        tp["e"]["GW_1"] = tp["f"]["GW_1"] = None
        tp["e"]["GW_2"], tp["f"]["GW_2"] = None, 2
        tp["e"]["GW_3"] = tp["f"]["GW_3"] = None
        tp["e"]["GW_4"] = tp["f"]["GW_4"] = None
        tp["e"]["GW_5"] = tp["f"]["GW_5"] = None
        tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = None
        tp["e"]["GW_age_2"], tp["f"]["GW_age_2"] = (
            None,
            12,
        )  # not specified in TSR data package (12 is "default" says Cosmin Man)
        tp["e"]["GW_age_3"] = tp["f"]["GW_age_3"] = None
        tp["e"]["GW_age_4"] = tp["f"]["GW_age_4"] = None
        tp["e"]["GW_age_5"] = tp["f"]["GW_age_5"] = None
        tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 17.5
    else:
        assert False  # bad leading species
    tp["e"]["AU"] = tp["e"]["TBLno"] = 10000 + au_id
    tp["f"]["AU"] = tp["f"]["TBLno"] = 20000 + au_id
    # si = au_data['ss'].SITE_INDEX.median()
    si = compute_vdyp_site_index(vdyp_out)
    # si /= (au_data['ss'].SITE_INDEX / au_data['ss'].siteprod).median()
    # si = au_data['ss'].siteprod.median()
    tp["e"]["SI"] = tp["f"]["SI"] = round(si, 1)
    tp["e"]["BEC"] = tp["f"]["BEC"] = au_data["ss"].BEC_ZONE_CODE.iloc[0]
    oaf1 = compute_vdyp_oaf1(vdyp_out)
    tp["e"]["OAF1"] = tp["f"]["OAF1"] = oaf1
    tp["e"]["OAF2"] = tp["f"]["OAF2"] = 0.95
    tp["e"]["FIZ"] = tp["f"]["FIZ"] = "I"
    tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
    tp["e"]["Proportion"] = tp["f"]["Proportion"] = 1

    return tp


def tipsy_params_tsa24(au_id, au_data, vdyp_out):
    tp = {"e": {}, "f": {}}
    spp_1 = list(au_data["species"].keys())[0]
    si = compute_vdyp_site_index(vdyp_out)
    bec = au_data["ss"].BEC_ZONE_CODE.iloc[0]
    tp["e"]["SI"] = tp["f"]["SI"] = si
    tp["e"]["BEC"] = tp["f"]["BEC"] = bec
    tp["e"]["AU"] = tp["e"]["TBLno"] = 10000 + au_id
    tp["f"]["AU"] = tp["f"]["TBLno"] = 20000 + au_id
    oaf1 = compute_vdyp_oaf1(vdyp_out)
    tp["e"]["OAF1"] = tp["f"]["OAF1"] = oaf1
    tp["e"]["OAF2"] = tp["f"]["OAF2"] = 0.95
    tp["e"]["FIZ"] = tp["f"]["FIZ"] = "I"
    tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
    tp["e"]["Proportion"] = tp["f"]["Proportion"] = 1
    tp["e"]["GW_3"] = tp["f"]["GW_3"] = None
    tp["e"]["GW_4"] = tp["f"]["GW_4"] = None
    tp["e"]["GW_5"] = tp["f"]["GW_5"] = None
    tp["e"]["GW_age_3"] = tp["f"]["GW_age_3"] = None
    tp["e"]["GW_age_4"] = tp["f"]["GW_age_4"] = None
    tp["e"]["GW_age_5"] = tp["f"]["GW_age_5"] = None
    tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 17.5
    if bec == "SBS":
        if spp_1 in species_pine:
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
            tp["e"]["Density"], tp["f"]["Density"] = 5700, 1700
            tp["e"]["Regen_Method"] = "N"
            tp["e"]["SPP_1"], tp["f"]["SPP_1"] = "PL", "PL"
            tp["e"]["SPP_2"], tp["f"]["SPP_2"] = "SW", "SW"
            tp["e"]["SPP_3"], tp["f"]["SPP_3"] = "BL", None
            tp["e"]["SPP_4"], tp["f"]["SPP_4"] = "FDI", None
            tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
            tp["e"]["PCT_1"], tp["f"]["PCT_1"] = 69, 67
            tp["e"]["PCT_2"], tp["f"]["PCT_2"] = 13, 33
            tp["e"]["PCT_3"], tp["f"]["PCT_3"] = 11, None
            tp["e"]["PCT_4"], tp["f"]["PCT_4"] = 7, None
            tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
            tp["e"]["GW_1"], tp["f"]["GW_1"] = None, 2
            tp["e"]["GW_2"], tp["f"]["GW_2"] = None, 18
            tp["e"]["GW_age_1"], tp["f"]["GW_age_1"] = (
                None,
                12,
            )  # not specified in TSR data package (12 is "default" says Cosmin Man)
            tp["e"]["GW_age_2"], tp["f"]["GW_age_2"] = (
                None,
                12,
            )  # not specified in TSR data package (12 is "default" says Cosmin Man)
        elif spp_1 in species_spruce:
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
            tp["e"]["Density"], tp["f"]["Density"] = 1600, 1600
            tp["e"]["SPP_1"], tp["f"]["SPP_1"] = "SW", "SW"
            tp["e"]["SPP_2"], tp["f"]["SPP_2"] = "PL", "PL"
            tp["e"]["SPP_3"], tp["f"]["SPP_3"] = "FDI", "FDI"
            tp["e"]["SPP_4"], tp["f"]["SPP_4"] = "BL", None
            tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
            tp["e"]["PCT_1"], tp["f"]["PCT_1"] = 55, 55
            tp["e"]["PCT_2"], tp["f"]["PCT_2"] = 38, 38
            tp["e"]["PCT_3"], tp["f"]["PCT_3"] = 5, 7
            tp["e"]["PCT_4"], tp["f"]["PCT_4"] = 2, None
            tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
            tp["e"]["GW_1"], tp["f"]["GW_1"] = 18, 18
            tp["e"]["GW_2"], tp["f"]["GW_2"] = 1, 1
            tp["e"]["GW_age_1"], tp["f"]["GW_age_1"] = (
                12,
                12,
            )  # not specified in TSR data package (12 is "default" says Cosmin Man)
            tp["e"]["GW_age_2"], tp["f"]["GW_age_2"] = (
                12,
                12,
            )  # not specified in TSR data package (12 is "default" says Cosmin Man)
        elif spp_1 in species_cedar:
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
            tp["e"]["Density"] = tp["f"]["Density"] = 2200
            tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "SW"
            tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "PL"
            tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "FDI"
            tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = "BL"
            tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
            tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 55
            tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 21
            tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 16
            tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = 8
            tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
            tp["e"]["GW_1"] = tp["f"]["GW_1"] = 21
            tp["e"]["GW_2"] = tp["f"]["GW_2"] = 2
            tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = (
                12  # not specified in TSR data package (12 is "default" says Cosmin Man)
            )
            tp["e"]["GW_age_2"] = tp["f"]["GW_age_2"] = (
                12  # not specified in TSR data package (12 is "default" says Cosmin Man)
            )
        elif spp_1 in species_fir:
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
            tp["e"]["Density"] = tp["f"]["Density"] = 2500
            tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "SW"
            tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "PL"
            tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "BL"
            tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = "FDI"
            tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
            tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 57
            tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 25
            tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 10
            tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = 8
            tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
            tp["e"]["GW_1"] = tp["f"]["GW_1"] = 15
            tp["e"]["GW_2"] = tp["f"]["GW_2"] = 1
            tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = (
                12  # not specified in TSR data package (12 is "default" says Cosmin Man)
            )
            tp["e"]["GW_age_2"] = tp["f"]["GW_age_2"] = (
                12  # not specified in TSR data package (12 is "default" says Cosmin Man)
            )
        elif spp_1 in species_douglasfir:
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
            tp["e"]["Density"] = tp["f"]["Density"] = 1600
            tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "FDI"
            tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = None
            tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = None
            tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = None
            tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
            tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 100
            tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = None
            tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = None
            tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = None
            tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
            tp["e"]["GW_1"] = tp["f"]["GW_1"] = None
            tp["e"]["GW_2"] = tp["f"]["GW_2"] = None
            tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = None
            tp["e"]["GW_age_2"] = tp["f"]["GW_age_2"] = None
        else:
            print(spp_1)
            assert False  # bad species
    elif bec == "ESSF":
        if spp_1 in species_fir:
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
            tp["e"]["Density"] = tp["f"]["Density"] = 1500
            tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "SE"
            tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "PL"
            tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "BL"
            tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = None
            tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
            tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 73
            tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 21
            tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 6
            tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = None
            tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
            tp["e"]["GW_1"] = tp["f"]["GW_1"] = 12
            tp["e"]["GW_2"] = tp["f"]["GW_2"] = 2
            tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = (
                12  # not specified in TSR data package (12 is "default" says Cosmin Man)
            )
            tp["e"]["GW_age_2"] = tp["f"]["GW_age_2"] = (
                12  # not specified in TSR data package (12 is "default" says Cosmin Man)
            )
        elif spp_1 in species_spruce:
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
            tp["e"]["Density"] = tp["f"]["Density"] = 1500
            tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "SE"
            tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "PL"
            tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "BL"
            tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = None
            tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
            tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 82
            tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 13
            tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 5
            tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = None
            tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
            tp["e"]["GW_1"] = tp["f"]["GW_1"] = 18
            tp["e"]["GW_2"] = tp["f"]["GW_2"] = 2
            tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = (
                12  # not specified in TSR data package (12 is "default" says Cosmin Man)
            )
            tp["e"]["GW_age_2"] = tp["f"]["GW_age_2"] = (
                12  # not specified in TSR data package (12 is "default" says Cosmin Man)
            )
        elif spp_1 in species_pine:
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
            tp["e"]["Density"] = tp["f"]["Density"] = 2900
            tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "PL"
            tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "BL"
            tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "SE"
            tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = None
            tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
            tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 62
            tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 21
            tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 17
            tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = None
            tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
            tp["e"]["GW_1"] = tp["f"]["GW_1"] = 1
            tp["e"]["GW_2"] = tp["f"]["GW_2"] = 13
            tp["e"]["GW_age_1"] = tp["f"]["GW_age_1"] = (
                12  # not specified in TSR data package (12 is "default" says Cosmin Man)
            )
            tp["e"]["GW_age_2"] = tp["f"]["GW_age_2"] = (
                12  # not specified in TSR data package (12 is "default" says Cosmin Man)
            )
            tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 12.5
        else:
            print(spp_1)
            assert False  # bad species
    else:
        print(bec)
        assert False  # bad BEC zone
    return tp


def tipsy_params_tsa40(au_id, au_data, vdyp_out):
    tp = {"e": {}, "f": {}}
    spp_1 = list(au_data["species"].keys())[0]
    si = compute_vdyp_site_index(vdyp_out)
    bec = au_data["ss"].BEC_ZONE_CODE.iloc[0]
    tp["e"]["SI"] = tp["f"]["SI"] = si
    tp["e"]["BEC"] = tp["f"]["BEC"] = bec
    tp["e"]["AU"] = tp["e"]["TBLno"] = 10000 + au_id
    tp["f"]["AU"] = tp["f"]["TBLno"] = 20000 + au_id
    oaf1 = compute_vdyp_oaf1(vdyp_out)
    tp["e"]["OAF1"] = tp["f"]["OAF1"] = oaf1
    tp["e"]["OAF2"] = tp["f"]["OAF2"] = 0.95
    tp["e"]["FIZ"] = tp["f"]["FIZ"] = "I"
    tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
    tp["e"]["Proportion"] = tp["f"]["Proportion"] = 1
    tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = (
        17.5 if spp_1 not in [species_pine] else 12.5
    )
    spp_pct = [(spp, au_data["species"][spp]["pct"]) for spp in au_data["species"]]
    for i in range(1, 6):
        try:
            spp, pct = spp_pct[i - 1]
            if spp == "SX":
                spp = "SW"
        except Exception:
            spp = pct = None
        for j in ["e", "f"]:
            tp[j]["SPP_%i" % i] = spp
            tp[j]["PCT_%i" % i] = pct
            tp[j]["GW_%i" % i] = None
            tp[j]["GW_age_%i" % i] = None

    if bec == "BWBS":
        if spp_1 in species_aspen:
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
            tp["e"]["Density"] = tp["f"]["Density"] = 4444
            tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = (
                "N"  # TSR data package says to use 'N', but then stands break up very early suddenly
            )
        elif spp_1 in species_pine:
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
            tp["e"]["Density"] = tp["f"]["Density"] = 1348
            tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
        elif spp_1 in species_spruce:
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
            tp["e"]["Density"] = tp["f"]["Density"] = 1167
            tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
        else:
            print("bad species", spp_1)
            assert False
    elif bec == "ESSF":
        if spp_1 in species_pine:
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
            tp["e"]["Density"] = tp["f"]["Density"] = 1186
            tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
        elif spp_1 in species_spruce:
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
            tp["e"]["Density"] = tp["f"]["Density"] = 1070
            tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
        else:
            print("bad species", spp_1)
            assert False
    elif bec == "SWB":
        if spp_1 in species_pine:
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
            tp["e"]["Density"] = tp["f"]["Density"] = 1338
            tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
        elif spp_1 in species_spruce:
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 2
            tp["e"]["Density"] = tp["f"]["Density"] = 1338
            tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
        else:
            print("bad species", spp_1)
            assert False
    else:
        print("bad BEC", bec)
        assert False
    return tp


def tipsy_params_tsa41(au_id, au_data, vdyp_out):
    tp = {"e": {}, "f": {}}
    si = compute_vdyp_site_index(vdyp_out)
    bec = au_data["ss"].BEC_ZONE_CODE.iloc[0]
    forest_type = au_data["ss"]["forest_type"].mode().iloc[0]
    tp["e"]["SI"] = tp["f"]["SI"] = si
    tp["e"]["BEC"] = tp["f"]["BEC"] = bec
    tp["e"]["AU"] = tp["e"]["TBLno"] = 10000 + au_id
    tp["f"]["AU"] = tp["f"]["TBLno"] = 20000 + au_id
    oaf1 = compute_vdyp_oaf1(vdyp_out)
    tp["e"]["OAF1"] = tp["f"]["OAF1"] = oaf1
    tp["e"]["OAF2"] = tp["f"]["OAF2"] = 0.95
    tp["e"]["FIZ"] = tp["f"]["FIZ"] = "I"
    tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
    tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "P"
    tp["e"]["Proportion"] = tp["f"]["Proportion"] = 1
    tp["e"]["SPP_5"] = tp["f"]["SPP_5"] = None
    tp["e"]["PCT_5"] = tp["f"]["PCT_5"] = None
    spp_pct = [(spp, au_data["species"][spp]["pct"]) for spp in au_data["species"]]
    spp_1, pct_1 = spp_pct[0]
    for i in range(1, 6):
        for j in ["e", "f"]:
            tp[j]["GW_%i" % i] = tp["f"]["GW_age_%i" % i] = None
    if spp_1 in species_spruce:
        if forest_type == 1:  # pure conifer
            tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "SW"
            tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "PL"
            tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "BL"
            tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = "AT"
            tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 63
            tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 21
            tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 17
            tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = 1
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
            tp["e"]["Density"] = tp["f"]["Density"] = 1335
        elif forest_type == 2:  # conifer mix
            assert False
            tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "BL"
            tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "BL"
            tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = ""
            tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = "AT"
            tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 63
            tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 21
            tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 17
            tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = 1
            tp["e"]["Regen_Delay"] = tp["f"]["Regen_Delay"] = 1
            tp["e"]["Density"] = tp["f"]["Density"] = 1335
        else:
            print(spp_pct)
            assert False  # not implemented (don't need to?)
        tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 17.5
    elif spp_1 in species_fir:
        if forest_type == 1:  # pure conifer
            tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "SW"
            tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "BL"
            tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "PL"
            tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = "AT"
            tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 64
            tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 29
            tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 6
            tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = 1
            tp["e"]["Density"] = tp["f"]["Density"] = 1064
        else:
            assert False  # not implemented (don't need to?)
        tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 17.5
    elif spp_1 in species_pine:
        if forest_type == 1:  # pure conifer
            tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "PL"
            tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = "SW"
            tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = "BL"
            tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = "AT"
            tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 63
            tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = 27
            tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = 8
            tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = 2
            tp["e"]["Density"] = tp["f"]["Density"] = 1219
        else:
            assert False  # not implemented (don't need to?)
        tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 12.5
    elif spp_1 in species_aspen:
        if forest_type == 4:  # pure conifer
            tp["e"]["SPP_1"] = tp["f"]["SPP_1"] = "AT"
            tp["e"]["SPP_2"] = tp["f"]["SPP_2"] = None
            tp["e"]["SPP_3"] = tp["f"]["SPP_3"] = None
            tp["e"]["SPP_4"] = tp["f"]["SPP_4"] = None
            tp["e"]["PCT_1"] = tp["f"]["PCT_1"] = 100
            tp["e"]["PCT_2"] = tp["f"]["PCT_2"] = None
            tp["e"]["PCT_3"] = tp["f"]["PCT_3"] = None
            tp["e"]["PCT_4"] = tp["f"]["PCT_4"] = None
            tp["e"]["Density"] = tp["f"]["Density"] = 3134
            tp["e"]["Regen_Method"] = tp["f"]["Regen_Method"] = "N"
        else:
            assert False  # not implemented (don't need to?)
        tp["e"]["Util_DBH_cm"] = tp["f"]["Util_DBH_cm"] = 12.5
    else:
        print("bad species", spp_1)
        assert False
    return tp


def build_tipsy_exclusion():
    """Return legacy per-TSA exclusion predicates and species filters."""
    return tipsy_exclusion


def get_legacy_tipsy_builders():
    """Return legacy in-code TIPSY parameter builders keyed by TSA."""
    return {
        "08": tipsy_params_tsa08,
        "16": tipsy_params_tsa16,
        "24": tipsy_params_tsa24,
        "40": tipsy_params_tsa40,
        "41": tipsy_params_tsa41,
    }

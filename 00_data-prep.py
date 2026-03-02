# Auto-generated from 00_data-prep.ipynb

# --- cell 3 ---
import os
import matplotlib.pyplot as plt

# import datatable

import pandas as pd
import geopandas as gpd
import pickle
import seaborn as sns
from shapely.ops import unary_union, Polygon
import numpy as np
from numpy.polynomial import Polynomial
import csv
from scipy.optimize import curve_fit
import rasterio as rio
from rasterio.plot import show
from rasterio.mask import mask
from rasterio.io import MemoryFile
from geocube.api.core import make_geocube
import subprocess
from rasterio.plot import show, show_hist
import warnings
from pympler import asizeof

# import ipcmagic
import ipyparallel as ipp
import mapply
import fiona
import affine

# from osgeo import gdal
from scipy.optimize import curve_fit as _curve_fit
from functools import partial, wraps
import itertools
from pathlib import Path
import sys

try:
    from femic.pipeline.bundle import (
        assign_curve_ids_from_au_table,
        build_bundle_tables_from_curves,
        bundle_tables_ready,
        ensure_scsi_au_from_table,
        load_bundle_tables,
        resolve_bundle_paths,
        write_bundle_tables,
    )
    from femic.pipeline.legacy_runtime import build_legacy_01a_runtime_config
    from femic.pipeline.io import (
        build_legacy_data_artifact_paths,
        build_ria_vri_checkpoint_paths,
    )
    from femic.pipeline.vdyp import build_vdyp_cache_paths
    from femic.pipeline.stages import (
        initialize_legacy_tsa_stage_state,
        load_legacy_module,
        prepare_tsa_index,
        run_legacy_tsa_loop,
        should_skip_if_outputs_exist,
    )
    from femic.pipeline.tsa import (
        assign_au_ids_from_scsi,
        assign_thlb_area_and_flag,
        assign_si_levels_from_stratum_quantiles,
        assign_stratum_matches_from_au_table,
        emit_missing_au_mapping_warning,
        summarize_missing_au_mappings,
        validate_nonempty_au_assignment,
    )
    from femic.pipeline.tipsy import (
        tipsy_params_excel_path,
        tipsy_stage_output_paths,
    )
    from femic.pipeline.stands import (
        DEFAULT_STANDS_PROP_NAMES,
        DEFAULT_STANDS_PROP_TYPES,
        build_stands_column_map,
        export_stands_shapefiles,
        should_skip_stands_export,
    )
except ModuleNotFoundError:
    _src_dir = Path(__file__).resolve().parent / "src"
    if _src_dir.is_dir():
        sys.path.insert(0, str(_src_dir))
    from femic.pipeline.bundle import (
        assign_curve_ids_from_au_table,
        build_bundle_tables_from_curves,
        bundle_tables_ready,
        ensure_scsi_au_from_table,
        load_bundle_tables,
        resolve_bundle_paths,
        write_bundle_tables,
    )
    from femic.pipeline.legacy_runtime import build_legacy_01a_runtime_config
    from femic.pipeline.io import (
        build_legacy_data_artifact_paths,
        build_ria_vri_checkpoint_paths,
    )
    from femic.pipeline.vdyp import build_vdyp_cache_paths
    from femic.pipeline.stages import (
        initialize_legacy_tsa_stage_state,
        load_legacy_module,
        prepare_tsa_index,
        run_legacy_tsa_loop,
        should_skip_if_outputs_exist,
    )
    from femic.pipeline.tsa import (
        assign_au_ids_from_scsi,
        assign_thlb_area_and_flag,
        assign_si_levels_from_stratum_quantiles,
        assign_stratum_matches_from_au_table,
        emit_missing_au_mapping_warning,
        summarize_missing_au_mappings,
        validate_nonempty_au_assignment,
    )
    from femic.pipeline.tipsy import (
        tipsy_params_excel_path,
        tipsy_stage_output_paths,
    )
    from femic.pipeline.stands import (
        DEFAULT_STANDS_PROP_NAMES,
        DEFAULT_STANDS_PROP_TYPES,
        build_stands_column_map,
        export_stands_shapefiles,
        should_skip_stands_export,
    )

# --- cell 5 ---
pd.set_option(
    "display.max_rows", 300
)  # bump this parameter up if you want to see more table rows
pd.set_option(
    "display.max_columns", 30
)  # bump this parameter up if you want to see more table rows

warnings.filterwarnings("ignore", message=".*initial implementation of Parquet.*")
# Swifter can speed up row-wise apply, but it has been unstable in this pipeline context.
# Default to plain pandas apply; allow explicit opt-in via FEMIC_USE_SWIFTER=1.
_use_swifter = os.environ.get("FEMIC_USE_SWIFTER", "0") == "1"
if _use_swifter:
    import swifter

    swifter.set_defaults(
        scheduler="synchronous",
        progress_bar=False,
        allow_dask_on_strings=False,
    )


def _row_apply(df, func, axis=1):
    if _use_swifter:
        return df.swifter.apply(func, axis=axis)
    return df.apply(func, axis=axis)


# --- cell 7 ---
# %ipcluster --help
# %load_ext ipyparallel
# %ipcluster start -n 16
_disable_ipp = os.environ.get("FEMIC_DISABLE_IPP", "1").strip().lower() in (
    "1",
    "true",
    "yes",
)
if _disable_ipp:
    print("ipyparallel disabled (FEMIC_DISABLE_IPP=1); using serial execution")
    _use_ipp = False
else:
    try:
        rc = ipp.Client()
        lbview = rc.load_balanced_view()
        _use_ipp = True
    except Exception as e:
        print("ipyparallel not available, falling back to serial execution:", e)
        _use_ipp = False

if not _use_ipp:

    class _SerialView:
        def map_async(self, func, *iterables, ordered=True):
            return [func(*args) for args in zip(*iterables)]

    class _SerialClient:
        def wait_interactive(self):
            return None

        def __len__(self):
            return 1

    rc = _SerialClient()
    lbview = _SerialView()

# --- cell 9 ---
_repo_root = Path(__file__).resolve().parent
_external_data_env = os.environ.get("FEMIC_EXTERNAL_DATA_ROOT")
_external_data_candidates = [
    Path(_external_data_env) if _external_data_env else None,
    (_repo_root / "data"),
    (_repo_root / ".." / "data"),
    (Path.home() / "data"),
]
_external_data_candidates = [p for p in _external_data_candidates if p is not None]


def _select_external_data_root():
    vri_rel = Path("bc/vri/2019/VEG_COMP_LYR_R1_POLY.gdb")
    for _candidate in _external_data_candidates:
        _candidate = _candidate.resolve()
        if (_candidate / vri_rel).exists():
            return _candidate
    return _external_data_candidates[0].resolve()


_external_data_root = _select_external_data_root()
vri_vclr1p_path = _external_data_root / "bc/vri/2019/VEG_COMP_LYR_R1_POLY.gdb"
_legacy_data_paths = build_legacy_data_artifact_paths()
ria_stands_path = _legacy_data_paths.ria_stands_path
tsa_boundaries_path = _external_data_root / "bc/tsa/FADM_TSA.gdb"
ria_maptiles_path = "ria_maptiles.csv"
vdyp_input_pandl_path = _legacy_data_paths.vdyp_input_pandl_path

site_prod_bc_gdb_path = (
    _legacy_data_paths.site_prod_bc_gdb_path
)  # ESRI File Geodatabase containing 22 species-wise site productivity raster layers

tsa_boundaries_feather_path = _legacy_data_paths.tsa_boundaries_feather_path
_ria_vri_checkpoint_paths = build_ria_vri_checkpoint_paths()
ria_vri_vclr1p_checkpoint1_feather_path = _ria_vri_checkpoint_paths[1]
ria_vri_vclr1p_checkpoint2_feather_path = _ria_vri_checkpoint_paths[2]
ria_vri_vclr1p_checkpoint3_feather_path = _ria_vri_checkpoint_paths[3]
ria_vri_vclr1p_checkpoint4_feather_path = _ria_vri_checkpoint_paths[4]
ria_vri_vclr1p_checkpoint5_feather_path = _ria_vri_checkpoint_paths[5]
ria_vri_vclr1p_checkpoint6_feather_path = _ria_vri_checkpoint_paths[6]
ria_vri_vclr1p_checkpoint7_feather_path = _ria_vri_checkpoint_paths[7]
ria_vri_vclr1p_checkpoint8_feather_path = _ria_vri_checkpoint_paths[8]
vri_vclr1p_categorical_columns_path = _legacy_data_paths.vri_vclr1p_categorical_columns_path
ria_vclr1p_feature_tif_path = _legacy_data_paths.ria_vclr1p_feature_tif_path

arc_raster_rescue_exe_path = Path("../ArcRasterRescue/build/arc_raster_rescue.exe")
siteprod_gdb_path = _legacy_data_paths.siteprod_gdb_path
siteprod_tmpexport_tif_path_prefix = _legacy_data_paths.siteprod_tmpexport_tif_path_prefix
siteprod_tif_path = _legacy_data_paths.siteprod_tif_path

vdyp_ply_feather_path = _legacy_data_paths.vdyp_ply_feather_path
vdyp_lyr_feather_path = _legacy_data_paths.vdyp_lyr_feather_path
vdyp_results_tsa_pickle_path_prefix = _legacy_data_paths.vdyp_results_tsa_pickle_path_prefix
vdyp_results_pickle_path = _legacy_data_paths.vdyp_results_pickle_path
vdyp_curves_smooth_tsa_feather_path_prefix = (
    _legacy_data_paths.vdyp_curves_smooth_tsa_feather_path_prefix
)
vdyp_curves_smooth_feather_path = _legacy_data_paths.vdyp_curves_smooth_feather_path

tipsy_params_path_prefix = _legacy_data_paths.tipsy_params_path_prefix

_default_ria_tsas = ["08", "16", "24", "40", "41"]
_femic_tsa_list = os.environ.get("FEMIC_TSA_LIST")
if _femic_tsa_list:
    ria_tsas = [tsa.strip() for tsa in _femic_tsa_list.split(",") if tsa.strip()]
else:
    ria_tsas = _default_ria_tsas
_femic_resume = os.environ.get("FEMIC_RESUME", "0") == "1"
_femic_debug_rows_raw = os.environ.get("FEMIC_DEBUG_ROWS")
try:
    _femic_debug_rows = int(_femic_debug_rows_raw) if _femic_debug_rows_raw else None
except ValueError:
    _femic_debug_rows = None
_femic_no_cache = _femic_debug_rows is not None
_femic_resume_effective = _femic_resume and not _femic_no_cache
si_levels = ["L", "M", "H"]


def _apply_debug_rows(_df, _label=None):
    if not _femic_debug_rows:
        return _df
    if _label:
        print(f"debug: limiting VRI input rows to {_femic_debug_rows} ({_label})")
    else:
        print(f"debug: limiting VRI input rows to {_femic_debug_rows}")
    return _df.head(_femic_debug_rows).copy()


if _femic_no_cache:
    print("debug: disabling cached checkpoint reuse")

raster_pxw = raster_pxh = 100

tipsy_params_columns = [
    line.strip() for line in _legacy_data_paths.tipsy_params_columns_path.read_text().splitlines()
]

# --- cell 11 ---
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

# --- cell 13 ---
if not arc_raster_rescue_exe_path.is_file():
    # Notebook cell only built the tool; in script keep a no-op.
    pass

# --- cell 15 ---
import_tsa_boundaries_data = 0
if import_tsa_boundaries_data:
    tsa_boundaries = gpd.read_file(tsa_boundaries_path)
    tsa_boundaries = (
        tsa_boundaries[["TSA_NUMBER", "geometry"]]
        .loc[tsa_boundaries.TSA_NUMBER.isin(ria_tsas)]
        .dissolve(by="TSA_NUMBER")
    )
    tsa_boundaries["geometry"] = tsa_boundaries.geometry.simplify(
        tolerance=1000, preserve_topology=True
    )
    tsa_boundaries.to_feather(tsa_boundaries_feather_path)
else:
    tsa_boundaries = gpd.read_feather(tsa_boundaries_feather_path)

# tsa_extent_all = Polygon(unary_union(list(tsa_boundaries.geometry.values)).exterior)

# --- cell 17 ---
import_vri_vclr1p_data = 1 if _femic_no_cache else 0  # set to False to use cached data
if import_vri_vclr1p_data:
    print("loading VRI data from source")

    def load_vri_vclr1p(vri_vclr1p_path, tsa_code, tsa_mask, ignore_geometry=False):
        import geopandas as gpd  # local import required to play nice with ipp engines

        result = gpd.read_file(
            vri_vclr1p_path, mask=tsa_mask, ignore_geometry=ignore_geometry
        )
        result["tsa_code"] = tsa_code
        return result

    tsa_gdfs = lbview.map_async(
        load_vri_vclr1p,
        [vri_vclr1p_path for tsa in ria_tsas],
        ria_tsas,
        [tsa_boundaries.loc[tsa].geometry for tsa in ria_tsas],
        ordered=True,
    )
    rc.wait_interactive()
    ria_vri_vclr1p = pd.concat(tsa_gdfs, axis=0, ignore_index=True)
    ria_vri_vclr1p.to_feather(ria_vri_vclr1p_checkpoint1_feather_path)
else:
    print("loading VRI data from checkpoint1 feather")
    ria_vri_vclr1p = gpd.read_feather(ria_vri_vclr1p_checkpoint1_feather_path)
    ria_vri_vclr1p = _apply_debug_rows(ria_vri_vclr1p, "checkpoint1")

f = ria_vri_vclr1p


# Normalize TSA codes to zero-padded strings for consistent indexing.
def _normalize_tsa_code(_value):
    try:
        return f"{int(_value):02d}"
    except (TypeError, ValueError):
        return str(_value).zfill(2)


if "tsa_code" in f.columns:
    f["tsa_code"] = f["tsa_code"].apply(_normalize_tsa_code)

f = _apply_debug_rows(f, "checkpoint1")

# --- cell 19 ---
# map layer indices to layer species codes
result = subprocess.run(
    [arc_raster_rescue_exe_path, siteprod_gdb_path],
    capture_output=True,
)
siteprod_layerspecies = {
    int(i): vv[10:].upper()
    for i, vv in [
        v.strip().split(" ") for v in result.stdout.decode().split("\n")[1:] if v
    ]
}
siteprod_specieslayer = {
    vv[10:].upper(): int(i)
    for i, vv in [
        v.strip().split(" ") for v in result.stdout.decode().split("\n")[1:] if v
    ]
}

if not siteprod_tif_path.is_file():
    # export species-wise raster layers to 22 GeoTIFFs
    print("Extracting siteprod raster data from ESRI File Geodatabase...")
    for i, species in site_prod_bc_layerspecies.items():
        print("... processing species", species)
        layer_tif_path = (
            siteprod_tmpexport_tif_path_prefix.parent
            / f"{siteprod_tmpexport_tif_path_prefix.name}{species}.tif"
        )
        subprocess.run(
            [
                arc_raster_rescue_exe_path,
                site_prod_bc_gdb_path,
                str(i),
                layer_tif_path,
            ]
        )

    # stack species-wise raster layers into a single multi-band GeoTIFF
    file_list = sorted(
        siteprod_tmpexport_tif_path_prefix.parent.glob(
            f"{siteprod_tmpexport_tif_path_prefix.name}*.tif"
        )
    )
    with rio.open(file_list[0]) as src:  # patch with missing CRS metadata
        meta = src.meta
        meta.update(
            count=len(file_list), compress="lzw", crs=rio.crs.CRS({"init": "epsg:3005"})
        )  # BC Albers equal area geographic projection

    with rio.open(siteprod_tif_path, "w", **meta) as dst:
        print("\nStacking siteprod raster data into a single multiband GeoTIFF file...")
        for id, layer in enumerate(file_list, start=1):
            print("... processing species", siteprod_layerspecies[id - 1])
            with rio.open(layer) as src:
                dst.write_band(id, src.read(1))
            layer.unlink()  # delete intermediate GeoTIFF (not needed anymore)


# --- cell 21 ---
def siteprod_species_lookup(s):
    spp = {
        "AC": "AT",
        "PLI": "PL",
        "FDI": "FD",
        "S": "SW",
        "SXL": "SX",
        "ACT": "AT",
        "E": "EP",
        "P": "PL",
        "EA": "EP",
        "SXW": "SX",
        "W": "EP",  # ?
        "T": "LT",  # ?
        "L": "LT",
        "B": "BL",
        "ACB": "AT",
        "PJ": "PL",  # ?
        "WS": "EP",
        "LA": "LT",
        "AX": "AT",
        "BB": "BL",
        "H": "HW",
        "BM": "BL",
        "V": "DR",
        "F": "FD",
        "C": "CW",
        "XC": "PL",
        "XD": "SW",
        "X": "SW",
        "A": "AT",
        "D": "DR",
        "Z": "SW",
        "Q": "AT",
        "Y": "YC",
        "R": "DR",
        "G": "DR",
    }  # ?
    try:
        result = spp[s]
    except:
        try:
            result = spp[s[0]]
        except:
            print(s)
            assert False  # bad species code
    return result


species_list = list(
    set().union(*[ria_vri_vclr1p["SPECIES_CD_%i" % i].unique() for i in range(1, 7)])
)
species_list = [s for s in species_list if s is not None]

# --- cell 24 ---
process_checkpoint2 = 1 if _femic_no_cache else 0
if process_checkpoint2:
    for i in range(1, 7):
        f["SPECIES_CD_%i" % i].fillna("X", inplace=True)
        f["SPECIES_PCT_%i" % i].fillna(0, inplace=True)
    f["SOIL_NUTRIENT_REGIME"].fillna("X", inplace=True)
    f["SOIL_MOISTURE_REGIME_1"].fillna("X", inplace=True)
    f["SITE_POSITION_MESO"].fillna("X", inplace=True)
    f["BCLCS_LEVEL_3"].fillna("X", inplace=True)
    f["BCLCS_LEVEL_4"].fillna("X", inplace=True)
    f["BCLCS_LEVEL_5"].fillna("X", inplace=True)
    f["BEC_VARIANT"].fillna("X", inplace=True)
    f["LIVE_STAND_VOLUME_125"].fillna(0, inplace=True)
    f.LIVE_VOL_PER_HA_SPP1_125.fillna(0, inplace=True)
    f.LIVE_VOL_PER_HA_SPP2_125.fillna(0, inplace=True)
    f.LIVE_VOL_PER_HA_SPP3_125.fillna(0, inplace=True)
    f.LIVE_VOL_PER_HA_SPP4_125.fillna(0, inplace=True)
    f.LIVE_VOL_PER_HA_SPP5_125.fillna(0, inplace=True)
    f.LIVE_VOL_PER_HA_SPP6_125.fillna(0, inplace=True)
    f = f[f.BCLCS_LEVEL_2 == "T"]  # implies f.BCLCS_LEVEL_1 == 'V'
    # f = f[f.BCLCS_LEVEL_5 != 'OP']
    f = f[f.NON_PRODUCTIVE_CD != None]
    f = f[f.FOR_MGMT_LAND_BASE_IND == "Y"]
    f = f[~f.BEC_ZONE_CODE.isin(["BAFA", "IMA"])]
    f = f[f.PROJ_AGE_1 >= 30]
    f = f[f.BASAL_AREA >= 5]
    f = f[f.LIVE_STAND_VOLUME_125 >= 1]
    f.shape
    # vri_vclr1p_categorical_columns = open(vri_vclr1p_categorical_columns_path).read().split('\n')
    # for c in vri_vclr1p_categorical_columns:
    #    f[c] = f[c].astype('category')
    with rio.open(siteprod_tif_path) as src:

        def mean_siteprod(r):
            a, _ = mask(src, [r.geometry], crop=True)
            s = r.SPECIES_CD_1
            s = s if s in siteprod_specieslayer else siteprod_species_lookup(s)
            i = siteprod_specieslayer[s]
            aa = a[i]
            return np.mean(aa[aa > 0])

        f["siteprod"] = _row_apply(f, mean_siteprod, axis=1)
    f.to_feather(ria_vri_vclr1p_checkpoint2_feather_path)
else:
    print("loading VRI data from checkpoint2 feather")
    f = gpd.read_feather(ria_vri_vclr1p_checkpoint2_feather_path)
    f = _apply_debug_rows(f, "checkpoint2")

# --- cell 26 ---
f.reset_index(inplace=True)

# --- cell 27 ---
process_checkpoint3 = 1 if _femic_no_cache else 1
if process_checkpoint3:

    def compile_species_vol(df, species):
        return df.apply(
            lambda r: sum(
                r["LIVE_VOL_PER_HA_SPP%i_125" % i]
                for i in range(1, 7)
                if r["SPECIES_CD_%i" % i] == species
            ),
            axis=1,
        )

    cols = list(
        itertools.chain.from_iterable(
            ["LIVE_VOL_PER_HA_SPP%i_125" % i] + ["SPECIES_CD_%i" % i]
            for i in range(1, 7)
        )
    )
    f_ = f[cols]
    result = lbview.map_async(
        compile_species_vol, [f_] * len(species_list), species_list, ordered=True
    )
    rc.wait_interactive()

    for i, species in enumerate(species_list):
        print("compiling species", species)
        f["live_vol_per_ha_125_%s" % species] = result[i]
    f.to_feather(ria_vri_vclr1p_checkpoint3_feather_path)
else:
    print("loading VRI data from checkpoint3 feather")
    f = gpd.read_feather(ria_vri_vclr1p_checkpoint3_feather_path)
    f = _apply_debug_rows(f, "checkpoint3")


# --- cell 29 ---
def is_conif(species_code):
    # return True if species_code is coniferous species
    return species_code[:1] in ["B", "C", "F", "H", "J", "L", "P", "S", "T", "Y"]


def is_decid(species_code):
    # return True if species_code is deciduous species
    return species_code[:1] in ["A", "D", "E", "G", "M", "Q", "R", "U", "V", "W"]


def pconif(r):
    # return proportion of volume from coniferous species in record r
    return (
        sum(
            r["SPECIES_PCT_%i" % i]
            for i in range(1, 7)
            if is_conif(r["SPECIES_CD_%i" % i])
        )
        / 100.0
    )


def pdecid(r):
    # return proportion of volume from deciduous species in record r
    return (
        sum(
            r["SPECIES_PCT_%i" % i]
            for i in range(1, 7)
            if is_decid(r["SPECIES_CD_%i" % i])
        )
        / 100.0
    )


def classify_stand_cdm(r):
    # Classify stand (from VRI record r) as one of: conif (c), decid (d), or mixed (m), where
    #   c >= 80% softwood
    #   d >= 80% hardwood
    #   m otherwise
    if pconif(r) >= 0.8:
        return "c"
    elif pdecid(r) >= 0.8:
        return "d"
    else:
        return "m"


def classify_stand_forest_type(r):
    # to (approximately) match TSA 41 TSR data package AU regeneration logic
    if pconif(r) >= 0.75:
        return 1  # pure conif
    elif pconif(r) >= 0.50:
        return 2  # conif mix
    elif pconif(r) >= 0.25:
        return 3  # decid mix
    else:
        return 4  # pure decid


# --- cell 31 ---
def stratify_stand(r, lexmatch=False, lexmatch_fieldname_suffix="_lexmatch"):
    result = ""
    if lexmatch:
        result += 3 * r["BEC_ZONE_CODE%s" % lexmatch_fieldname_suffix]
        result += "_"
        # result += r.BCLCS_LEVEL_5
        # result += '_'
        result += 2 * r["SPECIES_CD_1%s" % lexmatch_fieldname_suffix]
        if r.BCLCS_LEVEL_4 == "TM" and r.SPECIES_CD_2 != None:
            result += "+" + r["SPECIES_CD_2%s" % lexmatch_fieldname_suffix]
    else:
        result += r.BEC_ZONE_CODE
        result += "_"
        # result += r.BCLCS_LEVEL_5
        # result += '_'
        result += r.SPECIES_CD_1
        if r.BCLCS_LEVEL_4 == "TM" and r.SPECIES_CD_2 != None:
            result += "+" + r.SPECIES_CD_2
    return result


# --- cell 33 ---
f["BEC_ZONE_CODE_lexmatch"] = f.BEC_ZONE_CODE.str.ljust(4, fillchar="x")
for i in range(1, 3):
    f["SPECIES_CD_%i_lexmatch" % i] = f["SPECIES_CD_%i" % i].str.ljust(4, "x")
    f["SPECIES_CD_%i_lexmatch" % i] = (
        f["SPECIES_CD_%i" % i].str[:1] + f["SPECIES_CD_%i" % i]
    )

stratify_stand = stratify_stand
stratify_stand_lexmatch = partial(stratify_stand, lexmatch=True)

f["stratum"] = _row_apply(f, stratify_stand, axis=1)
f["stratum_lexmatch"] = _row_apply(f, stratify_stand_lexmatch, axis=1)

# --- cell 34 ---
stratum_col = "stratum"

# --- cell 36 ---
# f['forest_type'] = f.reset_index().swifter.apply(classify_stand_forest_type, axis=1)
f["forest_type"] = f.apply(classify_stand_forest_type, axis=1)

# --- cell 38 ---
f.to_feather(ria_vri_vclr1p_checkpoint4_feather_path)

# --- cell 42 ---
# f = f.reset_index().set_index('tsa_code')

# --- cell 44 ---
_legacy_stage_state = initialize_legacy_tsa_stage_state()
vdyp_curves_smooth = _legacy_stage_state.vdyp_curves_smooth
vdyp_results = _legacy_stage_state.vdyp_results
tipsy_params = _legacy_stage_state.tipsy_params
tipsy_curves = _legacy_stage_state.tipsy_curves
scsi_au = _legacy_stage_state.scsi_au
au_scsi = _legacy_stage_state.au_scsi
results = _legacy_stage_state.results

# --- cell 52 ---
f = prepare_tsa_index(f_table=f, tsa_column="tsa_code")

# --- cell 54 ---
if 1:
    force_run_vdyp = 0
    _run01a_module = load_legacy_module(
        script_path=Path(__file__).with_name("01a_run-tsa.py"),
        module_name="run_tsa_01a",
    )

    def _should_skip_01a(tsa):
        vdyp_cache_paths = build_vdyp_cache_paths(
            tsa_code=tsa,
            vdyp_results_tsa_pickle_path_prefix=vdyp_results_tsa_pickle_path_prefix,
            vdyp_curves_smooth_tsa_feather_path_prefix=vdyp_curves_smooth_tsa_feather_path_prefix,
        )
        return should_skip_if_outputs_exist(
            resume_effective=_femic_resume_effective,
            output_paths=(
                tipsy_params_excel_path(
                    tsa=tsa,
                    tipsy_params_path_prefix=tipsy_params_path_prefix,
                ),
                vdyp_cache_paths["vdyp_curves_smooth_tsa_feather_path"],
            ),
            skip_message=f"resume: skipping 01a for tsa {tsa} (outputs exist)",
        )

    def _run_one_01a(tsa):
        stratum_col = "stratum"
        runtime_config = build_legacy_01a_runtime_config(
            tsa_code=tsa,
            resume_effective=_femic_resume_effective,
            force_run_vdyp=bool(force_run_vdyp),
            kwarg_overrides_for_tsa=None,
            vdyp_results_pickle_path=vdyp_results_pickle_path,
            vdyp_input_pandl_path=vdyp_input_pandl_path,
            vdyp_ply_feather_path=vdyp_ply_feather_path,
            vdyp_lyr_feather_path=vdyp_lyr_feather_path,
            tipsy_params_columns=tipsy_params_columns,
            tipsy_params_path_prefix=tipsy_params_path_prefix,
            vdyp_results_tsa_pickle_path_prefix=vdyp_results_tsa_pickle_path_prefix,
            vdyp_curves_smooth_tsa_feather_path_prefix=vdyp_curves_smooth_tsa_feather_path_prefix,
            vdyp_out_cache=globals().get("vdyp_out_cache"),
            curve_fit_impl=globals().get("_curve_fit"),
        )
        _run01a_module.run_tsa(
            tsa=tsa,
            stratum_col=stratum_col,
            f=f,
            si_levels=si_levels,
            results=results,
            vdyp_results=vdyp_results,
            vdyp_curves_smooth=vdyp_curves_smooth,
            scsi_au=scsi_au,
            au_scsi=au_scsi,
            tipsy_params=tipsy_params,
            si_levelquants=si_levelquants,
            species_list=species_list,
            runtime_config=runtime_config,
        )

    run_legacy_tsa_loop(
        tsa_list=ria_tsas[:],
        should_skip_fn=_should_skip_01a,
        run_one_fn=_run_one_01a,
    )

# --- cell 58 ---
# loop over tsas here and run notebook 01_run-tsa_step2
_run01b_module = load_legacy_module(
    script_path=Path(__file__).with_name("01b_run-tsa.py"),
    module_name="run_tsa_01b",
)


def _should_skip_01b(tsa):
    tipsy_curves_path, tipsy_sppcomp_path = tipsy_stage_output_paths(tsa=tsa)
    return should_skip_if_outputs_exist(
        resume_effective=_femic_resume_effective,
        output_paths=(
            tipsy_curves_path,
            tipsy_sppcomp_path,
        ),
        skip_message=f"resume: skipping 01b for tsa {tsa} (outputs exist)",
    )


def _run_one_01b(tsa):
    _run01b_module.run_tsa(
        tsa=tsa,
        results=results,
        au_scsi=au_scsi,
        tipsy_curves=tipsy_curves,
        vdyp_curves_smooth=vdyp_curves_smooth,
    )


run_legacy_tsa_loop(
    tsa_list=ria_tsas[:],
    should_skip_fn=_should_skip_01b,
    run_one_fn=_run_one_01b,
)

# --- cell 64 ---
canfi_map = {
    "AC": 1211,
    "AT": 1201,
    "BL": 304,
    "EP": 1303,
    "FDI": 500,
    "HW": 402,
    "PL": 204,
    "PLI": 204,
    "SB": 101,
    "SE": 104,
    "SW": 105,
    "SX": 100,
    "S": 100,
}


# --- cell 65 ---
def canfi_species(stratum_code):
    s = stratum_code.split("_")[-1].split("+")[0]
    result = canfi_map[s]
    return result


# --- cell 67 ---
bundle_paths = resolve_bundle_paths(
    base_dir=_legacy_data_paths.model_input_bundle_dir,
    ensure_dir=True,
)
_bundle_ready = bundle_tables_ready(paths=bundle_paths)


if _femic_resume_effective and _bundle_ready:
    au_table, curve_table, curve_points_table = load_bundle_tables(
        paths=bundle_paths,
        pd_module=pd,
        normalize_tsa_code_fn=_normalize_tsa_code,
    )
    ensure_scsi_au_from_table(
        au_table=au_table,
        scsi_au=scsi_au,
        normalize_tsa_code_fn=_normalize_tsa_code,
    )
else:
    _bundle_assembly = build_bundle_tables_from_curves(
        tsa_list=ria_tsas,
        vdyp_curves_smooth=vdyp_curves_smooth,
        tipsy_curves=tipsy_curves,
        scsi_au=scsi_au,
        canfi_species_fn=canfi_species,
        pd_module=pd,
        message_fn=print,
    )
    _missing_df = _bundle_assembly.missing_au_curve_mappings
    if not _missing_df.empty:
        print(
            "Warning: skipped VDYP curve combos without AU mapping "
            f"({len(_missing_df)} rows). Top 10:"
        )
        print(
            _missing_df.value_counts(["tsa", "stratum_code", "si_level"])
            .head(10)
            .to_string()
        )
    au_table = _bundle_assembly.au_table
    curve_table = _bundle_assembly.curve_table
    curve_points_table = _bundle_assembly.curve_points_table
    if "tsa" in au_table.columns:
        au_table["tsa"] = au_table["tsa"].apply(_normalize_tsa_code)
    ensure_scsi_au_from_table(
        au_table=au_table,
        scsi_au=scsi_au,
        normalize_tsa_code_fn=_normalize_tsa_code,
    )

    # --- cell 69 ---
    au_table.head()

    # --- cell 70 ---
    curve_table.head()

    # --- cell 71 ---
    curve_points_table.head()

    # --- cell 73 ---
    write_bundle_tables(
        paths=bundle_paths,
        au_table=au_table,
        curve_table=curve_table,
        curve_points_table=curve_points_table,
    )

# --- cell 77 ---
if not _femic_no_cache:
    f = gpd.read_feather(ria_vri_vclr1p_checkpoint1_feather_path)
    f = _apply_debug_rows(f, "checkpoint1-reload")

# --- cell 79 ---
with rio.open(_legacy_data_paths.misc_thlb_tif_path) as src:

    def mean_thlb(r):
        try:
            a, _ = mask(src, [r.geometry], crop=True)
        except:
            return 0
        return np.mean(a[a >= 0])

    f["thlb_raw"] = _row_apply(f, mean_thlb, axis=1)

# --- cell 83 ---
if 1:
    f = f[f.BCLCS_LEVEL_2 == "T"]  # implies f.BCLCS_LEVEL_1 == 'V'
    # f = f[f.NON_PRODUCTIVE_CD != None]
    f = f[f.FOR_MGMT_LAND_BASE_IND == "Y"]
    f = f[~f.BEC_ZONE_CODE.isin(["BAFA", "IMA"])]
    f = f[~f.SPECIES_CD_1.isnull()]
    f = f[~f.BCLCS_LEVEL_5.isnull()]
    f = f[~f.SITE_INDEX.isnull()]

# --- cell 85 ---
f.shape

# --- cell 87 ---
f["BEC_ZONE_CODE_lexmatch"] = f.BEC_ZONE_CODE.str.ljust(4, fillchar="x")
for i in range(1, 3):
    f["SPECIES_CD_%i_lexmatch" % i] = f["SPECIES_CD_%i" % i].str.ljust(4, "x")
    f["SPECIES_CD_%i_lexmatch" % i] = (
        f["SPECIES_CD_%i" % i].str[:1] + f["SPECIES_CD_%i" % i]
    )

stratify_stand = stratify_stand
stratify_stand_lexmatch = partial(stratify_stand, lexmatch=True)

f["stratum"] = _row_apply(f, stratify_stand, axis=1)
f["stratum_lexmatch"] = _row_apply(f, stratify_stand_lexmatch, axis=1)

# --- cell 88 ---
f.to_feather(ria_vri_vclr1p_checkpoint5_feather_path)

# --- cell 90 ---
stratum_col = "stratum"
f["%s_matched" % stratum_col] = None

# --- cell 93 ---
f = assign_stratum_matches_from_au_table(
    f_table=f,
    au_table=au_table,
    tsa_list=ria_tsas,
    stratum_col=stratum_col,
    message_fn=print,
)

# --- cell 95 ---
# si_levelquants={'L':[5, 20, 35], 'M':[35, 50, 65], 'H':[65, 80, 95]}
si_levelquants = {"L": [0, 20, 35], "M": [35, 50, 65], "H": [65, 80, 100]}

# --- cell 96 ---
f, stratum_si_stats = assign_si_levels_from_stratum_quantiles(
    f_table=f,
    si_levelquants=si_levelquants,
    stratum_matched_col="stratum_matched",
    site_index_col="SITE_INDEX",
    si_level_col="si_level",
    message_fn=print,
)


# --- cell 98/99 ---
f = assign_au_ids_from_scsi(
    f_table=f,
    scsi_au=scsi_au,
    tsa_col="tsa_code",
    stratum_matched_col="stratum_matched",
    si_level_col="si_level",
    au_col="au",
)

if f["au"].isnull().any():
    _missing = summarize_missing_au_mappings(
        f_table=f,
        au_col="au",
        tsa_col="tsa_code",
        stratum_matched_col="stratum_matched",
        si_level_col="si_level",
        top_n=10,
    )
    emit_missing_au_mapping_warning(summary=_missing, message_fn=print)

validate_nonempty_au_assignment(
    f_table=f,
    au_col="au",
    site_index_col="SITE_INDEX",
    stratum_matched_col="stratum_matched",
    si_level_col="si_level",
)

# --- cell 101 ---
f.shape

# --- cell 103 ---
f = f[~f.au.isnull()]

# --- cell 105 ---
f.shape

# --- cell 107 ---
f.to_feather(ria_vri_vclr1p_checkpoint6_feather_path)

# --- cell 108 ---
try:
    au_table.set_index("au_id", inplace=True)
except:
    pass


# --- cell 110 ---
f = assign_curve_ids_from_au_table(
    f_table=f,
    au_table=au_table,
    pd_module=pd,
    np_module=np,
    au_col="au",
    proj_age_col="PROJ_AGE_1",
    managed_curve_col="managed_curve_id",
    unmanaged_curve_col="unmanaged_curve_id",
    curve1_col="curve1",
    curve2_col="curve2",
    managed_age_cutoff=60,
)

# --- cell 114 ---
f.to_feather(ria_vri_vclr1p_checkpoint7_feather_path)

# --- cell 115 ---
if not _femic_no_cache:
    f = gpd.read_feather(ria_vri_vclr1p_checkpoint7_feather_path)
    f = _apply_debug_rows(f, "checkpoint7")

# --- cell 116 ---
f.thlb_raw.describe()

# --- cell 117 ---
f.thlb_raw.hist()

# --- cell 118 ---
f.reset_index(inplace=True)


# --- cell 119-122 ---
f = assign_thlb_area_and_flag(
    f_table=f,
    species_spruce=species_spruce,
    species_pine=species_pine,
    species_aspen=species_aspen,
    species_fir=species_fir,
    tsa_col="tsa_code",
    thlb_raw_col="thlb_raw",
    area_col="FEATURE_AREA_SQM",
    species_col="SPECIES_CD_1",
    site_index_col="SITE_INDEX",
    thlb_area_col="thlb_area",
    thlb_col="thlb",
)

# --- cell 123 ---
f.query("thlb == 1").groupby("tsa_code").FEATURE_AREA_SQM.sum() * 0.0001

# --- cell 124 ---
f.groupby("tsa_code").thlb_area.sum()


# --- cell 126 ---
f.to_feather(ria_vri_vclr1p_checkpoint8_feather_path)


columns = build_stands_column_map(
    prop_names=DEFAULT_STANDS_PROP_NAMES,
    prop_types=DEFAULT_STANDS_PROP_TYPES,
)

# --- cell 133 ---
_skip_stands_shp_raw = os.environ.get("FEMIC_SKIP_STANDS_SHP")
_skip_stands_shp = should_skip_stands_export(
    skip_raw=_skip_stands_shp_raw,
    default_skip=_femic_no_cache,
)
if _skip_stands_shp:
    print(
        "debug: skipping stand shapefile export (set FEMIC_SKIP_STANDS_SHP=0 to enable)"
    )
else:
    export_stands_shapefiles(
        tsa_list=ria_tsas[:],
        f_table=f,
        au_table=au_table,
        columns_map=columns,
        output_root=_legacy_data_paths.stands_shp_dir,
        pd_module=pd,
        message_fn=print,
    )

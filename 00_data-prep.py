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
import shlex
from rasterio.plot import show, show_hist
import warnings
from pympler import asizeof

# import ipcmagic
import ipyparallel as ipp
import mapply
import fiona
import affine

# from osgeo import gdal
import glob
import operator
import distance
from scipy.optimize import curve_fit as _curve_fit
from functools import partial, wraps
import itertools
import importlib.util
from pathlib import Path

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
vri_vclr1p_path = str(_external_data_root / "bc/vri/2019/VEG_COMP_LYR_R1_POLY.gdb")
ria_stands_path = "./data/veg_comp_lyr_r1_poly-ria.shp"
tsa_boundaries_path = str(_external_data_root / "bc/tsa/FADM_TSA.gdb/")
ria_maptiles_path = "ria_maptiles.csv"
vdyp_input_pandl_path = "./data/VEG_COMP_VDYP7_INPUT_POLY_AND_LAYER_2019.gdb"

site_prod_bc_gdb_path = "./data/Site_Prod_BC.gdb/"  # ESRI File Geodatabase containing 22 species-wise site productivity raster layers

tsa_boundaries_feather_path = "./data/tsa_boundaries.feather"
ria_vri_vclr1p_checkpoint1_feather_path = "./data/ria_vri_vclr1p_checkpoint1.feather"
ria_vri_vclr1p_checkpoint2_feather_path = "./data/ria_vri_vclr1p_checkpoint2.feather"
ria_vri_vclr1p_checkpoint3_feather_path = "./data/ria_vri_vclr1p_checkpoint3.feather"
ria_vri_vclr1p_checkpoint4_feather_path = "./data/ria_vri_vclr1p_checkpoint4.feather"
ria_vri_vclr1p_checkpoint5_feather_path = "./data/ria_vri_vclr1p_checkpoint5.feather"
ria_vri_vclr1p_checkpoint6_feather_path = "./data/ria_vri_vclr1p_checkpoint6.feather"
ria_vri_vclr1p_checkpoint7_feather_path = "./data/ria_vri_vclr1p_checkpoint7.feather"
ria_vri_vclr1p_checkpoint8_feather_path = "./data/ria_vri_vclr1p_checkpoint8.feather"
vri_vclr1p_categorical_columns_path = "./data/vri_vclr1p_categorical_columns"
ria_vclr1p_feature_tif_path = "./data/ria_vclr1p_feature_raster.tif"

arc_raster_rescue_exe_path = "../ArcRasterRescue/build/arc_raster_rescue.exe"
siteprod_gdb_path = "./data/Site_Prod_BC.gdb/"
siteprod_tmpexport_tif_path_prefix = "./data/site_prod_bc_"
siteprod_tif_path = "./data/siteprod.tif"

vdyp_ply_feather_path = "./data/vdyp_ply.feather"
vdyp_lyr_feather_path = "./data/vdyp_lyr.feather"
vdyp_results_tsa_pickle_path_prefix = "./data/vdyp_results-tsa"
vdyp_results_pickle_path = "./data/vdyp_results.pkl"
vdyp_curves_smooth_tsa_feather_path_prefix = "./data/vdyp_curves_smooth-tsa"
vdyp_curves_smooth_feather_path = "./data/vdyp_curves_smooth.feather"

tipsy_params_path_prefix = "./data/tipsy_params_tsa"

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
    line.strip() for line in open("./data/tipsy_params_columns").readlines()
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
if not os.path.isfile(arc_raster_rescue_exe_path):
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
    shlex.split("%s %s" % (arc_raster_rescue_exe_path, siteprod_gdb_path)),
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

if not os.path.isfile(siteprod_tif_path):
    # export species-wise raster layers to 22 GeoTIFFs
    print("Extracting siteprod raster data from ESRI File Geodatabase...")
    for i, species in site_prod_bc_layerspecies.items():
        print("... processing species", species)
        args = "%s %s %i %s" % (
            arc_raster_rescue_exe_path,
            site_prod_bc_gdb_path,
            i,
            "%s%s.tif" % (siteprod_tmpexport_tif_path_prefix, species),
        )
        subprocess.run(shlex.split(args))

    # stack species-wise raster layers into a single multi-band GeoTIFF
    file_list = sorted(glob.glob("%s*.tif" % siteprod_tmpexport_tif_path_prefix))
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
            os.remove(layer)  # delete intermediate GeoTIFF (not needed anymore)


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

# --- cell 39 ---
if 0:  # roll back if screwed up further down
    f = gpd.read_feather(ria_vri_vclr1p_checkpoint4_feather_path)
    f = _apply_debug_rows(f, "checkpoint4")

# --- cell 42 ---
# f = f.reset_index().set_index('tsa_code')

# --- cell 44 ---
vdyp_curves_smooth = {}
vdyp_results = {}
tipsy_params = {}
tipsy_curves = {}
scsi_au = {}
au_scsi = {}
results = {}

# --- cell 45 ---
if 0:

    def process_vdyp_out(
        vdyp_out,
        volume_flavour="Vdwb",
        min_age=30,
        max_age=300,
        sigma_c1=10,
        sigma_c2=0.4,
        dx_c1=0.5,
        dx_c2=10,
        window=10,
        skip1=0,
        skip2=30,
        maxfev=100000,
        body_fit_func=body_fit_func,
        body_fit_func_bounds_func=body_fit_func_bounds_func,
        toe_fit_func=toe_fit_func,
        toe_fit_func_bounds_func=toe_fit_func_bounds_func,
    ):
        vdyp_out_concat = pd.concat(
            [v for v in vdyp_out.values() if type(v) == pd.core.frame.DataFrame]
        )
        c = vdyp_out_concat.groupby(level="Age")[volume_flavour].median()
        c = c[c > 0]
        c = c[c.index >= min_age]
        x = c.index.values
        y = c.rolling(window=window, center=True).median().values
        x, y = x[y > 0], y[y > 0]
        x, y = x[skip1:], y[skip1:]
        # return x, y
        y_mai = pd.Series(y / x, x)
        y_mai_max_age = y_mai.idxmax()
        sigma = (np.abs(x - y_mai_max_age) + sigma_c1) ** sigma_c2
        popt, pcov = curve_fit(
            body_fit_func,
            x,
            y,
            bounds=body_fit_func_bounds_func(x),
            maxfev=maxfev,
            sigma=sigma,
        )
        x = np.array(range(1, max_age))
        y = fit_func1(x, *popt)
        dx = max(0, dx_c1 * popt[2] - dx_c2)
        print(dx, dx_c1, popt[2], dx_c2)
        x, y, (i1, popt_toe) = fill_curve_left(
            x,
            y,
            skip=skip2,
            dx=dx,
            maxfev=maxfev,
            toe_fit_func=toe_fit_func,
            toe_fit_func_bounds_func=toe_fit_func_bounds_func,
        )
        print(popt_toe)
        return x, y


# --- cell 47 ---
kwarg_overrides = {
    "08": {
        ("BWBS_SB", "H"): {"skip1": 30},
        ("BWBS_S", "L"): {"skip1": 50},
        ("SWB_S", "L"): {"skip1": 30},
        ("BWBS_AT", "H"): {"skip1": 30},
    },
    "16": {("SWB_SX", "L"): {"skip1": 30}},
    "24": {("ESSF_BL", "L"): {"skip1": 30}},
    "40": {
        ("BWBS_SX", "L"): {"skip1": 30},
        ("SWB_SX", "L"): {"skip1": 60, "dx_c1": 1.0, "dx_c2": 0.0},
    },
    "41": {("ESSF_BL", "L"): {"skip1": 60}, ("ESSF_SE", "M"): {"skip1": 30}},
}

# --- cell 48 ---
if 0:
    tsa = "41"
    vdyp_curves_smooth_tsa_feather_path = "%s%s.feather" % (
        vdyp_curves_smooth_tsa_feather_path_prefix,
        tsa,
    )
    # if not os.path.isfile(vdyp_curves_smooth_tsa_feather_path):
    if 1:
        figsize = (8, 6)
        plot = 1
        vdyp_smoothxy = {}
        palette_flavours = ["RdPu", "Blues", "Greens", "Greys"]
        palette = sns.color_palette("Greens", 3)
        sns.set_palette(palette)
        alphas = [1.0, 0.5, 0.1]
        for stratumi, sc, result in results[tsa]:
            if sc != "ESSF_SE":
                continue
            if plot:
                fig, ax = plt.subplots(1, 1, figsize=figsize)
            print("stratum", stratumi, sc)
            # for i, si_level in enumerate(si_levels):
            for i, si_level in enumerate(["M"]):
                print("processing", sc, si_level)
                vdyp_out = vdyp_results[tsa][stratumi][si_level]
                kwargs = {}
                if (sc, si_level) in kwarg_overrides[tsa]:
                    kwargs.update(kwarg_overrides[tsa][(sc, si_level)])
                x, y = process_vdyp_out(vdyp_out, **kwargs)
                df = pd.DataFrame(zip(x, y), columns=["age", "volume"])
                df = df[df.volume > 0]
                df["stratum_code"] = sc
                df["si_level"] = si_level
                vdyp_smoothxy[(sc, si_level)] = df
                if plot:
                    vdyp_out_concat = pd.concat(
                        [
                            v
                            for v in vdyp_out.values()
                            if type(v) == pd.core.frame.DataFrame
                        ]
                    )
                    c = vdyp_out_concat.groupby(level="Age")["Vdwb"].median()
                    c = c[c > 0]
                    c = c[c.index >= 30]
                    x_ = c.index.values
                    y_ = c.values
                    plt.plot(
                        x_,
                        y_,
                        linestyle=":",
                        label="VDYP->agg (%s %s)" % (sc, si_level),
                        linewidth=2,
                        color=palette[i],
                    )
                    plt.plot(x, y, label="%s %s" % (sc, si_level))
            if plot:
                plt.legend()
                plt.xlim([0, 300])
                plt.ylim([0, 600])
                plt.tight_layout()
        vdyp_curves_smooth[tsa] = pd.concat(
            vdyp_smoothxy.values()
        ).reset_index()  # .set_index(['stratum_code', 'si_level'])
        vdyp_curves_smooth[tsa].to_feather(vdyp_curves_smooth_tsa_feather_path)
    # else:
    #    vdyp_curves_smooth[tsa] = pd.read_feather(vdyp_curves_smooth_tsa_feather_path)

# --- cell 49 ---
if 0:
    vdyp_out_cache = pickle.load(open("vdyp_out_cache.pkl", "rb"))

# --- cell 50 ---
if 0:
    force_run_vdyp = 0
    # tsa = '08' # fix bwbs sb h
    tsa = "16"
    # tsa = '24'
    # tsa = '40' # fix bwbs sx l
    # tsa = '41'
    stratum_col = "stratum"

# --- cell 52 ---
f.set_index("tsa_code", inplace=True)

# --- cell 54 ---
if 1:
    force_run_vdyp = 0
    for tsa in ria_tsas[:]:
        if _femic_resume_effective:
            _tipsy_params_path = f"{tipsy_params_path_prefix}{tsa}.xlsx"
            _vdyp_curves_path = (
                f"{vdyp_curves_smooth_tsa_feather_path_prefix}{tsa}.feather"
            )
            if os.path.isfile(_tipsy_params_path) and os.path.isfile(_vdyp_curves_path):
                print(f"resume: skipping 01a for tsa {tsa} (outputs exist)")
                continue
        stratum_col = "stratum"
        if "_run01a_module" not in globals():
            _path = Path(__file__).with_name("01a_run-tsa.py")
            _spec = importlib.util.spec_from_file_location("run_tsa_01a", _path)
            _run01a_module = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_run01a_module)
        _run01a_module.__dict__.update(globals())
        _run01a_module.tsa = tsa
        _run01a_module.stratum_col = stratum_col
        _run01a_module.run_tsa()

# --- cell 55 ---
if 0:
    pickle.dump(vdyp_out_cache, open("vdyp_out_cache.pkl", "wb"))

# --- cell 58 ---
# loop over tsas here and run notebook 01_run-tsa_step2
for tsa in ria_tsas[:]:
    if _femic_resume_effective:
        _tipsy_curves_path = f"./data/tipsy_curves_tsa{tsa}.csv"
        _tipsy_spp_path = f"./data/tipsy_sppcomp_tsa{tsa}.csv"
        if os.path.isfile(_tipsy_curves_path) and os.path.isfile(_tipsy_spp_path):
            print(f"resume: skipping 01b for tsa {tsa} (outputs exist)")
            continue
    if "_run01b_module" not in globals():
        _path = Path(__file__).with_name("01b_run-tsa.py")
        _spec = importlib.util.spec_from_file_location("run_tsa_01b", _path)
        _run01b_module = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_run01b_module)
    _run01b_module.__dict__.update(globals())
    _run01b_module.tsa = tsa
    _run01b_module.run_tsa()

# --- cell 62 ---
if 0:
    spp_map = pd.read_csv("./data/LandR_sppEquivalencies.csv")
    spp_map = spp_map[
        (~spp_map["LANDIS_traits"].isnull()) & (~spp_map["BC_Forestry"].isnull())
    ][["BC_Forestry", "LANDIS_traits"]]
    spp_map["vri"] = spp_map["BC_Forestry"].str.upper()
    spp_map["link"] = spp_map["LANDIS_traits"]
    canfi = pd.read_csv("./data/canfi_species.csv")
    canfi["link"] = canfi.genus + "." + canfi.species
    canfi = canfi.set_index("link").merge(
        spp_map[["link", "vri"]], on="link", how="left"
    )
    canfi = canfi[~canfi.vri.isnull()].set_index("vri")

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
_bundle_dir = Path("./data/model_input_bundle")
_active_bundle_dir = _bundle_dir
_required_bundle_files = ("au_table.csv", "curve_table.csv", "curve_points_table.csv")

os.makedirs(_active_bundle_dir, exist_ok=True)

_au_table_path = _active_bundle_dir / "au_table.csv"
_curve_table_path = _active_bundle_dir / "curve_table.csv"
_curve_points_path = _active_bundle_dir / "curve_points_table.csv"
_bundle_ready = (
    _au_table_path.is_file()
    and _curve_table_path.is_file()
    and _curve_points_path.is_file()
)


def _ensure_scsi_au_from_table(_au_table):
    for _row in _au_table.itertuples(index=False):
        _tsa = _normalize_tsa_code(_row.tsa)
        _tsa_map = scsi_au.setdefault(_tsa, {})
        _key = (str(_row.stratum_code), str(_row.si_level))
        if _key in _tsa_map:
            continue
        _au_base = int(_row.au_id) - 100000 * int(_tsa)
        _tsa_map[_key] = _au_base


if _femic_resume_effective and _bundle_ready:
    au_table = pd.read_csv(_au_table_path)
    curve_table = pd.read_csv(_curve_table_path)
    curve_points_table = pd.read_csv(_curve_points_path)
    if "tsa" in au_table.columns:
        au_table["tsa"] = au_table["tsa"].apply(_normalize_tsa_code)
    _ensure_scsi_au_from_table(au_table)
else:
    au_table_data = {
        "au_id": [],
        "tsa": [],
        "stratum_code": [],
        "si_level": [],
        "canfi_species": [],
        "unmanaged_curve_id": [],
        "managed_curve_id": [],
    }

    curve_table_data = {"curve_id": [], "curve_type": []}

    curve_points_table_data = {"curve_id": [], "x": [], "y": []}

    missing_au_curve_mappings = []
    for tsa in ria_tsas:
        print(tsa)
        vdyp_curves_ = vdyp_curves_smooth[tsa].set_index(["stratum_code", "si_level"])
        tipsy_curves_ = tipsy_curves[tsa].reset_index().set_index("AU")
        for stratum_code, si_level in list(vdyp_curves_.index.unique()):
            scsi_key = (str(stratum_code), str(si_level))
            au_id_ = scsi_au.get(tsa, {}).get(scsi_key)
            if au_id_ is None:
                missing_au_curve_mappings.append(
                    {"tsa": tsa, "stratum_code": stratum_code, "si_level": si_level}
                )
                continue
            tipsy_curve_id = 20000 + au_id_
            is_managed_au = tipsy_curve_id in tipsy_curves_.index.unique()
            au_id = 100000 * int(tsa) + au_id_
            unmanaged_curve_id = au_id
            managed_curve_id = au_id + 20000 if is_managed_au else unmanaged_curve_id
            # print(au_id, stratum_code, si_level, is_managed_au, unmanaged_curve_id, managed_curve_id)
            au_table_data["au_id"].append(au_id)
            au_table_data["tsa"].append(tsa)
            au_table_data["stratum_code"].append(stratum_code)
            au_table_data["si_level"].append(si_level)
            au_table_data["canfi_species"].append(canfi_species(stratum_code))
            au_table_data["unmanaged_curve_id"].append(unmanaged_curve_id)
            curve_table_data["curve_id"].append(unmanaged_curve_id)
            curve_table_data["curve_type"].append("unmanaged")
            vdyp_curve = vdyp_curves_.loc[(stratum_code, si_level)]
            # print('vdyp curve')
            for x, y in zip(vdyp_curve.age, vdyp_curve.volume):
                # print(x, round(y, 2))
                curve_points_table_data["curve_id"].append(unmanaged_curve_id)
                curve_points_table_data["x"].append(int(x))
                curve_points_table_data["y"].append(round(y, 2))
            au_table_data["managed_curve_id"].append(managed_curve_id)
            if is_managed_au:
                curve_table_data["curve_id"].append(managed_curve_id)
                curve_table_data["curve_type"].append("managed")
                tipsy_curve = tipsy_curves_.loc[tipsy_curve_id]
                # print('tipsy curve')
                for x, y in zip(tipsy_curve.Age, tipsy_curve.Yield):
                    # print(x, round(y, 2))
                    curve_points_table_data["curve_id"].append(managed_curve_id)
                    curve_points_table_data["x"].append(int(x))
                    curve_points_table_data["y"].append(round(y, 2))
    if missing_au_curve_mappings:
        _missing_df = pd.DataFrame(missing_au_curve_mappings)
        print(
            "Warning: skipped VDYP curve combos without AU mapping "
            f"({len(_missing_df)} rows). Top 10:"
        )
        print(
            _missing_df.value_counts(["tsa", "stratum_code", "si_level"])
            .head(10)
            .to_string()
        )
    au_table = pd.DataFrame(au_table_data)
    curve_table = pd.DataFrame(curve_table_data)
    curve_points_table = pd.DataFrame(curve_points_table_data)
    if "tsa" in au_table.columns:
        au_table["tsa"] = au_table["tsa"].apply(_normalize_tsa_code)
    _ensure_scsi_au_from_table(au_table)

    # --- cell 69 ---
    au_table.head()

    # --- cell 70 ---
    curve_table.head()

    # --- cell 71 ---
    curve_points_table.head()

    # --- cell 73 ---
    au_table.to_csv(_au_table_path)
    curve_table.to_csv(_curve_table_path)
    curve_points_table.to_csv(_curve_points_path)

# --- cell 77 ---
if not _femic_no_cache:
    f = gpd.read_feather(ria_vri_vclr1p_checkpoint1_feather_path)
    f = _apply_debug_rows(f, "checkpoint1-reload")

# --- cell 79 ---
with rio.open("./data/misc.thlb.tif") as src:

    def mean_thlb(r):
        try:
            a, _ = mask(src, [r.geometry], crop=True)
        except:
            return 0
        return np.mean(a[a >= 0])

    f["thlb_raw"] = _row_apply(f, mean_thlb, axis=1)

# --- cell 81 ---
if 0:
    thlb_rasterprop_thresh = 0.01
    with rio.open("./data/ria_demo/ria_landscapestack_init.tif") as src:

        def is_thlb(r):
            try:
                a, _ = mask(src, [r.geometry], crop=True)
            except:
                return 0
            aa = a[1]
            return 1 if np.mean(aa[aa >= 0]) > thlb_rasterprop_thresh else 0

        f["thlb"] = _row_apply(f, is_thlb, axis=1)

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

# --- cell 89 ---
if 0:
    f = pd.read_feather(ria_vri_vclr1p_checkpoint5_feather_path)
    f = _apply_debug_rows(f, "checkpoint5")

# --- cell 90 ---
stratum_col = "stratum"
f["%s_matched" % stratum_col] = None

# --- cell 91 ---
if 0:
    au_table = pd.read_csv(f"{_active_bundle_dir}/au_table.csv")
    curve_table = pd.read_csv(f"{_active_bundle_dir}/curve_table.csv")
    curve_points_table = pd.read_csv(f"{_active_bundle_dir}/curve_points_table.csv")
    au_table["tsa"] = au_table.apply(lambda r: "%02d" % r.tsa, axis=1)

# --- cell 93 ---
for tsa in ria_tsas:
    print("matching tsa", tsa)
    try:
        f.reset_index(inplace=True)
    except:
        pass
    stratum_codes = list(au_table.set_index("tsa").loc[tsa].stratum_code.unique())
    f_ = f.set_index("tsa_code").loc[tsa].set_index("stratum")
    totalarea = f_.FEATURE_AREA_SQM.sum()
    f_["totalarea_p"] = f_.FEATURE_AREA_SQM / totalarea
    names1 = set(f_.loc[stratum_codes].stratum_lexmatch.unique())
    names2 = set(f_.stratum_lexmatch.unique()) - names1
    stratum_key = (
        f_.reset_index().groupby("%s_lexmatch" % stratum_col)[stratum_col].first()
    )
    totalarea_p_sum__ = f_.groupby("%s_lexmatch" % stratum_col).totalarea_p.sum()
    lev_dist = {
        n2: {n1: distance.levenshtein(n1, n2) for n1 in names1} for n2 in names2
    }
    lev_dist_low = {
        n2: {
            n1: (lev_dist[n2][n1], totalarea_p_sum__.loc[n1])
            for n1 in lev_dist[n2].keys()
            if lev_dist[n2][n1] == min(lev_dist[n2].values())
        }
        for n2 in names2
    }
    bm = {
        stratum_key.loc[n2]: stratum_key[
            max(lev_dist_low[n2].items(), key=operator.itemgetter(1))[0]
        ]
        for n2 in names2
    }
    f_.reset_index(inplace=True)
    c, sc = stratum_col, stratum_codes
    f_["%s_matched" % stratum_col] = _row_apply(
        f_,
        lambda r: r[c] if r[c] in sc else bm[r[c]], axis=1
    )

    m = (
        f[["FEATURE_ID"]]
        .merge(f_[["FEATURE_ID", "stratum_matched"]], on="FEATURE_ID", how="left")
        .set_index("FEATURE_ID")
    )
    f.set_index("FEATURE_ID", inplace=True)
    f["stratum_matched"] = m.stratum_matched.where(
        ~m.stratum_matched.isnull(), f.stratum_matched
    )

# --- cell 95 ---
stratum_si_stats = f.groupby("stratum_matched").SITE_INDEX.describe(
    percentiles=[0, 0.05, 0.20, 0.35, 0.5, 0.65, 0.80, 0.95, 1]
)
# si_levelquants={'L':[5, 20, 35], 'M':[35, 50, 65], 'H':[65, 80, 95]}
si_levelquants = {"L": [0, 20, 35], "M": [35, 50, 65], "H": [65, 80, 100]}

# --- cell 96 ---
for stratum_code in stratum_si_stats.index:
    print(stratum_code)
    for i, (si_level, Q) in enumerate(si_levelquants.items()):
        si_lo = stratum_si_stats.loc[stratum_code].loc["%i%%" % Q[0]]
        si_md = stratum_si_stats.loc[stratum_code].loc["%i%%" % Q[1]]
        si_hi = stratum_si_stats.loc[stratum_code].loc["%i%%" % Q[2]]
        f.loc[
            (f.stratum_matched == stratum_code)
            & (f.SITE_INDEX >= si_lo)
            & (f.SITE_INDEX <= si_hi),
            "si_level",
        ] = si_level


# --- cell 98 ---
def _lookup_scsi_au(tsa_code, stratum_code, si_level):
    tsa_map = scsi_au.get(str(tsa_code))
    if not tsa_map:
        return None
    return tsa_map.get((str(stratum_code), str(si_level)))


def au_from_scsi(r):
    au_base = _lookup_scsi_au(r.tsa_code, r.stratum_matched, r.si_level)
    if au_base is None:
        return None
    return 100000 * int(r.tsa_code) + au_base


# --- cell 99 ---
f["au"] = _row_apply(f, au_from_scsi, axis=1)

if f["au"].isnull().any():
    _missing = (
        f.loc[f["au"].isnull(), ["tsa_code", "stratum_matched", "si_level"]]
        .value_counts()
        .head(10)
    )
    print("Warning: missing AU mappings for some strata (top 10 shown):")
    print(_missing)

if f["au"].isnull().all():
    _null_summary = {
        "rows": int(len(f)),
        "site_index_null": int(f.SITE_INDEX.isnull().sum())
        if "SITE_INDEX" in f
        else None,
        "stratum_matched_null": int(f.stratum_matched.isnull().sum())
        if "stratum_matched" in f
        else None,
        "si_level_null": int(f.si_level.isnull().sum()) if "si_level" in f else None,
    }
    raise ValueError(
        "AU assignment produced no rows; check SITE_INDEX/stratum matching and "
        f"si_level assignment. Summary: {_null_summary}"
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
def assign_curve1(r):
    # age=60 managed/unmanaged cutoff assumption from Cosmin Man (personal communication)
    if pd.isna(r.au):
        return None
    au_id = int(r.au)
    if au_id not in au_table.index:
        return None
    au = au_table.loc[au_id]
    if r.PROJ_AGE_1 <= 60 and not np.isnan(au["managed_curve_id"]):
        curve_id = au["managed_curve_id"]
    else:
        curve_id = au["unmanaged_curve_id"]
    return int(curve_id)


# --- cell 111 ---
f["curve1"] = _row_apply(f, assign_curve1, axis=1)


# --- cell 112 ---
def assign_curve2(r):
    if pd.isna(r.au):
        return None
    au_id = int(r.au)
    if au_id not in au_table.index:
        return None
    au = au_table.loc[au_id]
    return au["unmanaged_curve_id"]


# --- cell 113 ---
f["curve2"] = _row_apply(f, assign_curve2, axis=1)

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


# --- cell 119 ---
def thlb_area(r):
    if r.tsa_code == "08":
        if r.thlb_raw < 90:
            return 0.0
        if r.SPECIES_CD_1 in species_spruce and r.SITE_INDEX < 10:
            return 0.0
        if r.SPECIES_CD_1 in species_pine and r.SITE_INDEX < 15:
            return 0.0
        if r.SPECIES_CD_1 in species_aspen and r.SITE_INDEX < 15:
            return 0.0
        if r.SPECIES_CD_1 in species_fir and r.SITE_INDEX < 10:
            return 0.0
        if r.SPECIES_CD_1 in ("SB", "E", "EA", "EB", "LT"):
            return 0
    return r.thlb_raw * r.FEATURE_AREA_SQM * 0.000001


# --- cell 120 ---
f["thlb_area"] = _row_apply(f, thlb_area, axis=1)


# --- cell 121 ---
def assign_thlb(r):
    thlb_thresh = 50
    if r.tsa_code == "08":
        thlb_thresh = 93
    elif r.tsa_code == "24":
        thlb_thresh = 69
    return 1 if r.thlb_raw > thlb_thresh else 0


# --- cell 122 ---
f["thlb"] = _row_apply(f, assign_thlb, axis=1)

# --- cell 123 ---
f.query("thlb == 1").groupby("tsa_code").FEATURE_AREA_SQM.sum() * 0.0001

# --- cell 124 ---
f.groupby("tsa_code").thlb_area.sum()


# --- cell 125 ---
def has_managed_curve(r):
    if r.thlb == 0:
        return -1
    else:
        if np.isnan(au_table.loc[int(r.au)].managed_curve_id):
            return 0
        else:
            return 1


# --- cell 126 ---
f.to_feather(ria_vri_vclr1p_checkpoint8_feather_path)

# --- cell 127 ---
if 0:
    f = gpd.read_feather(ria_vri_vclr1p_checkpoint8_feather_path)
    f = _apply_debug_rows(f, "checkpoint8")

# --- cell 128 ---
if 0:
    f.to_file("./data/ria_vri-final.shp")


# --- cell 129 ---
def clean_geometry(r):
    from shapely.geometry import MultiPolygon

    g = r.geometry
    if not g.is_valid:
        _g = g.buffer(0)
        ################################
        # HACK
        # Something changed (maybe in fiona?) and now all GDB datasets are
        # loading as MultiPolygon geometry type (instead of Polygon).
        # The buffer(0) trick smashes the geometry back to Polygon,
        # so this hack upcasts it back to MultiPolygon.
        #
        # Not sure how robust this is going to be (guessing not robust).
        _g = MultiPolygon([_g])
        assert _g.is_valid
        assert _g.geom_type == "MultiPolygon"
        g = _g
    return g


# --- cell 130 ---
def extract_features(f, tsa):
    f_ = f[
        [
            "geometry",
            "tsa_code",
            "thlb",
            "au",
            "curve1",
            "curve2",
            "SPECIES_CD_1",
            "PROJ_AGE_1",
            "FEATURE_AREA_SQM",
        ]
    ]
    f_ = f_.set_index("tsa_code").loc[tsa].reset_index()
    f_.geometry = f_.apply(clean_geometry, axis=1)
    return f_


# --- cell 131 ---
# prop_names = [u'tsa_code', u'thlb', u'au', u'SPECIES_CD_1', u'PROJ_AGE_1', u'FEATURE_AREA_SQM']
prop_names = [
    "tsa_code",
    "thlb",
    "au",
    "canfi_species",
    "PROJ_AGE_1",
    "FEATURE_AREA_SQM",
]
prop_types = [
    ("theme0", "str:10"),
    ("theme1", "str:1"),
    ("theme2", "str:10"),
    ("theme3", "str:5"),
    ("age", "int:5"),
    ("area", "float:10.1"),
]

# --- cell 132 ---
columns = dict(zip(prop_names, dict(prop_types).keys()))

# --- cell 133 ---
import os

_skip_stands_shp_raw = os.environ.get("FEMIC_SKIP_STANDS_SHP")
if _skip_stands_shp_raw is None:
    _skip_stands_shp = _femic_no_cache
else:
    _skip_stands_shp = _skip_stands_shp_raw.strip().lower() in ("1", "true", "yes")
if _skip_stands_shp:
    print("debug: skipping stand shapefile export (set FEMIC_SKIP_STANDS_SHP=0 to enable)")
else:
    for tsa in ria_tsas[:]:
        print("processing tsa", tsa)
        f_ = extract_features(f, tsa)
        try:
            os.mkdir("./data/shp/tsa%s.shp" % tsa)
        except:
            pass
        f_.rename(columns=columns, inplace=True)
        f_.theme0 = "tsa" + f_.theme0
        f_.theme2 = f_.theme2.astype(int)
        f_.theme3 = f_.apply(lambda r: au_table.loc[r.theme2].canfi_species, axis=1)
        f_.age = f_.age.fillna(0)
        f_.age = f_.age.astype(int)
        f_.area = (f_.area * 0.0001).round(1)
        f_.to_file("./data/shp/tsa%s.shp/stands.shp" % tsa)

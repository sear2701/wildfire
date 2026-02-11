import geopandas as gpd
import pandas as pd
import requests

# -----------------------------
# Settings
# -----------------------------
FIRE_NAME = "Deer Creek"
YEAR = 2025

# WFIGS 2025 Wildfire Perimeters (ArcGIS Feature Layer item)
# This is the authoritative perimeter dataset for 2025
# Ref: https://www.arcgis.com/home/item.html?id=f72ebe741e3b4f0db376b4e765728339
WFIGS_LAYER_QUERY_URL = (
    "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/"
    "WFIGS_Interagency_Perimeters/FeatureServer/0/query"
)

# Conversion constant
SQM_PER_ACRE = 4046.8564224

# -----------------------------
# 1) Query the Deer Creek Fire perimeter from WFIGS
# -----------------------------
params = {
    "where": f"IncidentName = '{FIRE_NAME}' AND FireYear = {YEAR}",
    "outFields": "*",
    "f": "geojson",
}

r = requests.get(WFIGS_LAYER_QUERY_URL, params=params)
r.raise_for_status()
geojson = r.json()

fire_gdf = gpd.GeoDataFrame.from_features(geojson["features"], crs="EPSG:4326")

if fire_gdf.empty:
    raise ValueError(f"No fire perimeter returned for IncidentName='{FIRE_NAME}', FireYear={YEAR}")

# Some datasets may include multiple perimeters (updates).
# A safe default: take the largest polygon as the "final-ish" perimeter.
fire_gdf["area_deg"] = fire_gdf.geometry.area
fire_perim = fire_gdf.sort_values("area_deg", ascending=False).iloc[[0]].drop(columns="area_deg")

# -----------------------------
# 2) Load US state boundaries (Census cartographic boundaries)
# -----------------------------
states_url = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_state_20m.zip"
states = gpd.read_file(states_url).to_crs("EPSG:4326")

# Keep just Utah + Colorado
states_subset = states[states["STUSPS"].isin(["UT", "CO"])].copy()

# -----------------------------
# 3) Reproject to equal-area projection (for correct area)
# -----------------------------
# EPSG:5070 = NAD83 / Conus Albers (good for US area calculations)
fire_perim_aea = fire_perim.to_crs("EPSG:5070")
states_subset_aea = states_subset.to_crs("EPSG:5070")

# -----------------------------
# 4) Intersect fire perimeter with each state boundary
# -----------------------------
intersection = gpd.overlay(states_subset_aea, fire_perim_aea, how="intersection")

# -----------------------------
# 5) Compute area in acres
# -----------------------------
intersection["area_sqm"] = intersection.geometry.area
intersection["area_acres"] = intersection["area_sqm"] / SQM_PER_ACRE

# Summarize by state
summary = (
    intersection.groupby("STUSPS")["area_acres"]
    .sum()
    .reset_index()
    .sort_values("area_acres", ascending=False)
)

print("Estimated Deer Creek Fire burned area by state (acres):")
print(summary)

print("\nTotal (UT+CO):", summary["area_acres"].sum())

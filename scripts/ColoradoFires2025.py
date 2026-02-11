import requests
import geopandas as gpd
import pandas as pd

# -----------------------------
# SETTINGS
# -----------------------------
YEAR = 2025
STATE = "CO"
MIN_ACRES = 1000
PAGE_SIZE = 1000

WFIGS_PERIM_LAYER_URL = (
    "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/"
    "WFIGS_Interagency_Perimeters/FeatureServer/0"
)
WFIGS_QUERY_URL = WFIGS_PERIM_LAYER_URL + "/query"

SQM_PER_ACRE = 4046.8564224


# -----------------------------
# Helpers
# -----------------------------
def get_layer_metadata(layer_url: str) -> dict:
    r = requests.get(layer_url, params={"f": "pjson"}, timeout=60)
    r.raise_for_status()
    return r.json()


def pick_field(fields, preferred_names):
    """Return the first matching field name (case-insensitive) from preferred_names."""
    name_map = {f["name"].lower(): f["name"] for f in fields}
    for cand in preferred_names:
        if cand.lower() in name_map:
            return name_map[cand.lower()]
    return None


def fetch_all_geojson_features(query_url: str, where: str, out_fields: str = "*", page_size: int = 1000):
    all_features = []
    offset = 0

    while True:
        params = {
            "where": where,
            "outFields": out_fields,
            "returnGeometry": "true",
            "f": "geojson",
            "resultRecordCount": page_size,
            "resultOffset": offset,
        }

        r = requests.get(query_url, params=params, timeout=120)
        r.raise_for_status()
        payload = r.json()

        if "error" in payload:
            raise RuntimeError(f"ArcGIS error response: {payload['error']} (URL: {r.url})")

        features = payload.get("features")
        if features is None:
            raise RuntimeError(
                "Response did not contain 'features'. "
                f"Top-level keys: {list(payload.keys())}. URL: {r.url}"
            )

        if len(features) == 0:
            break

        all_features.extend(features)
        offset += page_size

    return all_features


def ms_since_epoch(date_str_utc: str) -> int:
    """
    ArcGIS date fields are often stored as milliseconds since epoch.
    We can use DATE 'YYYY-MM-DD' in many ArcGIS where clauses instead, but not always.
    This helper is here if you need epoch ms later.
    """
    import datetime
    dt = datetime.datetime.fromisoformat(date_str_utc.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)


# -----------------------------
# 1) Inspect layer fields to build a valid WHERE clause
# -----------------------------
meta = get_layer_metadata(WFIGS_PERIM_LAYER_URL)
fields = meta.get("fields", [])
if not fields:
    raise RuntimeError("Could not read fields from layer metadata.")

field_names = [f["name"] for f in fields]
print("Layer field count:", len(field_names))
print("Some fields:", field_names[:30])

# Pick state field
state_field = pick_field(fields, ["POOSTATE", "STATE", "State", "IncidentState", "PooState"])
if state_field is None:
    raise RuntimeError(f"Could not find a state field. Available fields include: {field_names[:60]}")

# Try to pick a fire-year style field
year_field = pick_field(fields, ["FireYear", "FIREYEAR", "YEAR", "Year", "FYear", "FIRE_YEAR"])

# If no year field, fall back to a date field that exists
# Common perimeter date fields (vary widely):
date_field = None
if year_field is None:
    date_field = pick_field(
        fields,
        ["PerimeterDateTime", "DateCurrent", "CreateDate", "CreateDateTime",
         "ModifiedDate", "EditDate", "PolygonDateTime", "perimeterdatetime"]
    )

print("Chosen fields:")
print("  state_field =", state_field)
print("  year_field  =", year_field)
print("  date_field  =", date_field)

# Build WHERE clause
if year_field is not None:
    where = f"{year_field} = {YEAR} AND {state_field} = '{STATE}'"
else:
    if date_field is None:
        raise RuntimeError(
            "No FireYear-like field and no known date field found to filter by year. "
            "Print the fields above and pick an appropriate date field."
        )
    # Many ArcGIS services support SQL like:
    #   date_field >= DATE '2025-01-01' AND date_field < DATE '2026-01-01'
    where = (
        f"{state_field} = '{STATE}' AND "
        f"{date_field} >= DATE '{YEAR}-01-01' AND {date_field} < DATE '{YEAR+1}-01-01'"
    )

print("\nWHERE clause:")
print(where)

# -----------------------------
# 2) Fetch features (paged)
# -----------------------------
features = fetch_all_geojson_features(WFIGS_QUERY_URL, where=where, page_size=PAGE_SIZE)
print(f"\nDownloaded {len(features)} perimeter feature(s) matching query.")

if not features:
    raise ValueError("No perimeters returned. Try printing the WHERE clause URL and adjusting fields.")

perims = gpd.GeoDataFrame.from_features(features, crs="EPSG:4326")

# -----------------------------
# 3) Compute acres from geometry (equal-area projection)
# -----------------------------
perims_aea = perims.to_crs("EPSG:5070")
perims_aea["area_sqm_calc"] = perims_aea.geometry.area
perims_aea["acres_calc"] = perims_aea["area_sqm_calc"] / SQM_PER_ACRE

# -----------------------------
# 4) Choose final perimeter per fire name (largest polygon per name)
# -----------------------------
name_field = pick_field(fields, ["IncidentName", "FIRENAME", "FireName", "incidentname", "Incident_Nm"])
if name_field is None or name_field not in perims_aea.columns:
    # Fall back: use whatever looks name-like in the dataframe
    candidates = [c for c in perims_aea.columns if "name" in c.lower()]
    raise RuntimeError(f"Could not find fire name field. Name-like candidates: {candidates}")

final_perims = (
    perims_aea.sort_values("acres_calc", ascending=False)
    .drop_duplicates(subset=[name_field], keep="first")
    .copy()
)

# -----------------------------
# 5) Filter > 1000 acres and save results
# -----------------------------
big_fires = final_perims[final_perims["acres_calc"] > MIN_ACRES].copy()

big_fires_table = (
    big_fires[[name_field, "acres_calc"]]
    .rename(columns={name_field: "FireName", "acres_calc": "FinalAcres"})
    .sort_values("FinalAcres", ascending=False)
    .reset_index(drop=True)
)

print("\nColorado fires > 1000 acres in 2025 (final perimeter size estimate):")
print(big_fires_table.to_string(index=False))

out_csv = "colorado_2025_fires_gt1000ac_final_perimeter.csv"
big_fires_table.to_csv(out_csv, index=False)
print(f"\nSaved CSV: {out_csv}")

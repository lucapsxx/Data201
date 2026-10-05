
import argparse
import os
import time
 
import pandas as pd
import requests
from multiprocessing import Pool

# ---------------- CONFIG ----------------
API_KEY = os.environ.get("Fran Key", "247afde54abf4348ad4eb75e2e036b41")
DOMAIN = "koordinates.com"          # change if the layer lives on a different Koordinates site
LAYER_ID = 111227               # <-- fill in with the Stats NZ area-code layer ID
AREA_CODE_FIELD = "SA22023_V1_00"   # <-- fill in with the real field name (see test query output)
RADIUS_M = 100                      # search radius in metres around each point
MAX_RESULTS = 1
N_PROCESSES = 10                    # keep modest so you don't hammer the API / hit rate limits

INPUT_CSV = "data/airbnbcleaned.csv"      # must have 'latitude' and 'longitude' columns
OUTPUT_CSV = "data/airbnb_with_area_codes.csv"


BASE_URL = f"https://{DOMAIN}/services/query/v1/vector.json"
# -----------------------------------------


def query_point(lat, lon, max_retries=3, verbose=False):
    """Query the Vector Query API for one point. Returns the area code
    (or None if nothing found / all retries failed)."""
    params = {
        "key": API_KEY,
        "layer": LAYER_ID,
        "x": lon,
        "y": lat,
        "radius": RADIUS_M,
        "max_results": MAX_RESULTS,
        "geometry": "false",
        "with_field_names": "true",
    }

    for attempt in range(max_retries):
        try:
            resp = requests.get(BASE_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if verbose:
                print(data)

            layers = data.get("vectorQuery", {}).get("layers", {})
            features = layers.get(str(LAYER_ID), {}).get("features", [])
            if not features:
                return None
            return features[0]["properties"].get(AREA_CODE_FIELD)

        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Failed for ({lat}, {lon}): {e}")
                return None
            time.sleep(1 + attempt)  # simple backoff before retrying


def _query_row(row):
    """Helper for multiprocessing.Pool: row is (index, lat, lon)."""
    idx, lat, lon = row
    return idx, query_point(lat, lon)


def run_batch():
    if API_KEY == "YOUR_API_KEY_HERE":
        raise SystemExit("Set KOORDINATES_API_KEY (env var) or edit API_KEY in the script.")
    if LAYER_ID == 12345:
        raise SystemExit("Set LAYER_ID to the real Stats NZ layer ID before running the batch.")

    df = pd.read_csv(INPUT_CSV)
    rows = list(df[["latitude", "longitude"]].itertuples(name=None))  # (index, lat, lon)

    print(f"Querying {len(rows)} points against layer {LAYER_ID}...")

    results = {}
    with Pool(processes=N_PROCESSES) as pool:
        for i, (idx, area_code) in enumerate(pool.imap_unordered(_query_row, rows), 1):
            results[idx] = area_code
            if i % 100 == 0:
                print(f"  {i}/{len(rows)} done")

    df["area_code"] = df.index.map(results)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved to {OUTPUT_CSV}")

    missing = df["area_code"].isna().sum()
    if missing:
        print(f"Warning: {missing} rows got no match (outside radius, bad coords, etc.)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", nargs=2, type=float, metavar=("LAT", "LON"),
                         help="Test a single lat/lon query and print the raw response, "
                              "e.g. --test -36.8485 174.7633")
    args = parser.parse_args()

    if args.test:
        lat, lon = args.test
        if API_KEY == "YOUR_API_KEY_HERE":
            raise SystemExit("Set KOORDINATES_API_KEY (env var) or edit API_KEY in the script.")
        print(f"Testing query for lat={lat}, lon={lon}...")
        result = query_point(lat, lon, verbose=True)
        print(f"\nExtracted area code (field '{AREA_CODE_FIELD}'): {result}")
    else:
        run_batch()
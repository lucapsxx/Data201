"""D7: one-command Christchurch Airbnb update pipeline.

Install: python -m pip install pandas matplotlib

$env:KOORDINATES_API_KEY = "2e76914357a944f481dac26c8c936287"
python Ken_d7.py

Place the historical Airbnb file, cleaned tenancy file and listings_<month><year>.csv
beside this script. Add another monthly file and run the same command.
Area lookup adapted from teammate's d5_Fran.py (layer 111227, SA22023_V1_00).
API reference: https://help.koordinates.com/query-api-and-web-services/koordinates-query-api-non-technical-users/
AI assistance: ChatGPT helped orchestrate the supplied D5 and D6 scripts.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import re
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import json
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

LAYER_ID = 111227
AREA_FIELD = "SA22023_V1_00"
BASE_URL = "https://koordinates.com/services/query/v1/vector.json"
MONTHS = {name: i for i, name in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], 1)}
MONTHS.update({name[:3]: value for name, value in list(MONTHS.items())})


def read_csv(path):
    # String IDs avoid loss of precision for very large Airbnb identifiers.
    return pd.read_csv(path, dtype={"id": "string", "host_id": "string"})


def clean_listings(frame):
    frame = frame.loc[frame["neighbourhood_group"].eq("Christchurch City")].copy()
    frame["price"] = pd.to_numeric(
        frame["price"].astype("string").str.replace(r"[$,]", "", regex=True),
        errors="coerce")
    for column in ("latitude", "longitude"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["point_key"] = [
        f"{lat:.12f},{lon:.12f}" if pd.notna(lat) and pd.notna(lon) else None
        for lat, lon in zip(frame.latitude, frame.longitude)]
    return frame


def filename_month(path):
    match = re.fullmatch(r"listings_([A-Za-z]+)(\d{4})", path.stem)
    if not match or match[1].lower() not in MONTHS:
        raise ValueError(f"Use a filename such as listings_September2026.csv: {path.name}")
    return f"{match[2]}-{MONTHS[match[1].lower()]:02d}"


def query_point(item, api_key):
    point_key, lat, lon = item
    params = {"key": api_key, "layer": LAYER_ID, "x": lon, "y": lat,
              "radius": 100, "max_results": 1, "geometry": "false",
              "with_field_names": "true"}
    for attempt in range(3):
        try:
            with urlopen(BASE_URL + "?" + urlencode(params), timeout=20) as response:
                data = json.load(response)
            features = data.get("vectorQuery", {}).get("layers", {}).get(
                str(LAYER_ID), {}).get("features", [])
            code = features[0]["properties"].get(AREA_FIELD) if features else None
            return point_key, code
        except HTTPError as error:
            if error.code in (401, 403):
                raise RuntimeError("Koordinates rejected the API key or layer access.") from None
            if attempt < 2:
                time.sleep(attempt + 1)
        except (URLError, TimeoutError, ValueError, KeyError):
            # Do not print request URLs: they contain the private API key.
            if attempt < 2:
                time.sleep(attempt + 1)
    return point_key, None


def assign_area_codes(listings, historical, output_dir, workers, allow_partial):
    cache_path = output_dir / "area_code_cache.csv"
    known = historical[["point_key", "area_code"]].dropna()
    if cache_path.exists():
        known = pd.concat([known, pd.read_csv(cache_path)], ignore_index=True)
    conflicts = known.groupby("point_key")["area_code"].nunique()
    if (conflicts > 1).any():
        raise ValueError("Conflicting area codes for identical coordinates; check historical/cache data.")
    cache = known.drop_duplicates("point_key").set_index("point_key")["area_code"].to_dict()
    pending = listings.loc[~listings.point_key.isin(cache) & listings.point_key.notna(),
                           ["point_key", "latitude", "longitude"]].drop_duplicates("point_key")
    api_key = os.environ.get("KOORDINATES_API_KEY")
    if len(pending) and api_key:
        points = list(pending.itertuples(index=False, name=None))
        # Test one query before starting the concurrent batch, as requested in D5.
        first_key, first_code = query_point(points[0], api_key)
        if first_code is None:
            raise RuntimeError("The first area lookup returned no code. Check the key, layer and field.")
        cache[first_key] = first_code
        print(f"First query passed. Looking up {len(points) - 1} further unique locations...")
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for i, (key, code) in enumerate(executor.map(
                    lambda point: query_point(point, api_key), points[1:]), 1):
                if code is not None:
                    cache[key] = code
                if i % 100 == 0:
                    print(f"  {i}/{len(points) - 1} queried")
                    pd.Series(cache, name="area_code").rename_axis("point_key").to_csv(cache_path)
    pd.Series(cache, name="area_code").rename_axis("point_key").to_csv(cache_path)
    listings["area_code"] = pd.to_numeric(listings.point_key.map(cache), errors="coerce").astype("Int64")
    missing = listings[listings.area_code.isna()]
    missing.to_csv(output_dir / "unresolved_area_codes.csv", index=False)
    if len(missing) and not allow_partial:
        raise RuntimeError(
            f"{len(missing)} listing-month rows need area codes. Set KOORDINATES_API_KEY and rerun. "
            "Details are in outputs/unresolved_area_codes.csv. "
            "Use --allow-partial only for a clearly labelled incomplete preview.")
    return listings


def join_tenancy(listings, tenancy):
    # D6 analysis uses the ALL dwellings / ALL beds aggregate, not every category.
    tenancy = tenancy.loc[tenancy.dwelling_type.eq("ALL") &
                           tenancy.number_of_beds.eq("ALL")].copy()
    tenancy["location_id"] = pd.to_numeric(tenancy.location_id, errors="coerce").astype("Int64")
    tenancy["tenancy_quarter"] = pd.to_datetime(tenancy.timeframe, errors="raise")
    tenancy = tenancy.dropna(subset=["location_id"])
    if tenancy.duplicated(["location_id", "tenancy_quarter"]).any():
        raise ValueError("Duplicate ALL/ALL tenancy rows for an area and quarter.")
    pieces = []
    for month, rows in listings.groupby("MonthYear", sort=True):
        eligible = tenancy[tenancy.tenancy_quarter.le(pd.Timestamp(month + "-01"))]
        latest = eligible.sort_values("tenancy_quarter").drop_duplicates("location_id", keep="last")
        pieces.append(rows.merge(latest, how="left", left_on="area_code",
                                 right_on="location_id", validate="many_to_one"))
    merged = pd.concat(pieces, ignore_index=True)
    merged["difference"] = merged.price - pd.to_numeric(merged.geometric_mean_rent, errors="coerce") / 7
    return merged


def save_plots(merged, output_dir, partial):
    label = " — INCOMPLETE preview" if partial else ""
    price = merged.groupby(["MonthYear", "area_code"])["difference"].mean().unstack(0)
    price = price.loc[price.mean(axis=1).sort_values().index]
    price.to_csv(output_dir / "difference_by_area.csv")
    if price.empty:
        raise ValueError("No matched areas available for plotting.")
    ax = price.plot.bar(figsize=(16, 7), width=0.8)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set(xlabel="Stats NZ area code", ylabel="Airbnb nightly price − weekly rent / 7 (NZD)",
           title="Average price difference by area and Airbnb month" + label)
    ax.figure.text(0.01, 0.01, "Tenancy: latest available quarter on/before each Airbnb month; missing prices excluded.", fontsize=9)
    ax.figure.tight_layout(rect=(0, 0.04, 1, 1))
    ax.figure.savefig(output_dir / "difference_by_area.png", dpi=150)
    plt.close(ax.figure)
    # Count listing IDs, not names. Count each area's bonds once within a ward/month.
    matched = merged.dropna(subset=["area_code", "total_bonds"])
    counts = matched.groupby(["MonthYear", "neighbourhood", "area_code"]).agg(
        num_bnbs=("id", "nunique"), total_bonds=("total_bonds", "first")).reset_index()
    ward = counts.groupby(["MonthYear", "neighbourhood"])[["num_bnbs", "total_bonds"]].sum()
    ward["difference"] = ward.total_bonds - ward.num_bnbs
    ward.to_csv(output_dir / "bnb_vs_rental_by_ward.csv")
    ax = ward["difference"].unstack(0).plot.bar(figsize=(14, 7))
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set(xlabel="Neighbourhood (ward)", ylabel="Total bonds − number of Airbnb listings",
           title="Bonds versus Airbnb listings in matched areas, by month" + label)
    ax.figure.text(0.01, 0.01, "Latest available tenancy quarter; each area's bonds counted once per ward/month. Bonds are not total rental stock.", fontsize=9)
    ax.figure.tight_layout(rect=(0, 0.04, 1, 1))
    ax.figure.savefig(output_dir / "bnb_vs_rental_by_ward.png", dpi=150)
    plt.close(ax.figure)


def run_pipeline(data_dir, output_dir, workers=4, allow_partial=False):
    output_dir.mkdir(parents=True, exist_ok=True)
    historical = clean_listings(read_csv(data_dir / "airbnb_with_area_codes.csv"))
    if "month_year" not in historical:
        raise ValueError("Historical Airbnb data needs its original month_year column.")
    historical["MonthYear"] = pd.to_datetime(historical.month_year, errors="raise").dt.strftime("%Y-%m")
    historical["area_code"] = pd.to_numeric(historical.area_code, errors="coerce").astype("Int64")
    frames = [historical]
    for path in sorted(data_dir.glob("listings_*.csv")):
        rows = clean_listings(read_csv(path))
        rows["MonthYear"] = filename_month(path)
        rows["source_file"] = path.name
        frames.append(rows)
        print(f"{path.name}: {len(rows)} Christchurch City listings")
    if len(frames) == 1:
        raise ValueError("No listings_<month><year>.csv monthly files found.")
    listings = pd.concat(frames, ignore_index=True)
    if listings.duplicated(["id", "MonthYear"]).any():
        raise ValueError("Duplicate listing IDs within a month; check overlapping input files.")
    listings = assign_area_codes(listings, historical, output_dir, workers, allow_partial)
    tenancy = pd.read_csv(data_dir / "QuarterlyTenencyCleaned.csv")
    merged = join_tenancy(listings, tenancy)
    partial = listings.area_code.isna().any()
    merged["incomplete_area_coverage"] = partial
    merged.to_csv(output_dir / "merged_listings.csv", index=False)
    listings.drop(columns="point_key").to_csv(output_dir / "airbnb_all_months.csv", index=False)
    merged.groupby("MonthYear").agg(
        listings=("id", "size"), missing_area_codes=("area_code", lambda s: s.isna().sum()),
        missing_prices=("price", lambda s: s.isna().sum()),
        unmatched_tenancy=("total_bonds", lambda s: s.isna().sum()),
        median_airbnb_price=("price", "median")).to_csv(output_dir / "monthly_summary.csv")
    merged.isna().sum().rename("missing_count").to_csv(output_dir / "missing_counts.csv")
    merged.select_dtypes(include="number").describe().to_csv(output_dir / "numeric_summary.csv")
    save_plots(merged, output_dir, partial)
    print(f"Saved {len(merged)} listing-month rows and both graphs to {output_dir}")
    print("Tenancy quarters used:", merged.tenancy_quarter.dropna().dt.strftime("%Y-%m-%d").unique())
    if partial:
        print("INCOMPLETE PREVIEW: unresolved area codes are excluded from area/ward plots.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--allow-partial", action="store_true", help="Offline/incomplete preview only")
    args = parser.parse_args()
    if not 1 <= args.workers <= 10:
        parser.error("--workers must be between 1 and 10")
    try:
        run_pipeline(args.data_dir, args.output_dir or args.data_dir / "outputs",
                     args.workers, args.allow_partial)
    except (ValueError, RuntimeError, FileNotFoundError) as error:
        raise SystemExit(str(error))

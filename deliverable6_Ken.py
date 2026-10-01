"""Compare May 2026 Christchurch Airbnb listings with 2026 Q2 tenancy data.

Run from the directory containing both input CSVs. Generated files go in Ken_D6_output/.
The SA2 boundary versions must be confirmed before interpreting the comparison.

Week 9 references: Monday lecture slides 5, 9, 12-13, 16-19, 21;
Tuesday lecture slide 6 (human review of AI-assisted work).
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# Visible parameters and project-relative paths.
AIRBNB_PATH = Path("airbnb_with_area_codes.csv")
TENANCY_PATH = Path("QuarterlyTenencyCleaned.csv")
OUTPUT_DIR = Path("Ken_D6_output")
TENANCY_QUARTER = "2026-04-01"  # Quarter containing May 2026.
AIRBNB_MONTH = "2026-5"


def main():
    listings = pd.read_csv(AIRBNB_PATH)
    tenancy = pd.read_csv(TENANCY_PATH)
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Explicit expectations are checked in code.
    listings = listings.loc[
        listings["neighbourhood_group"].eq("Christchurch City")
        & listings["month_year"].eq(AIRBNB_MONTH)
    ].copy()
    if listings.empty or listings["id"].duplicated().any():
        raise ValueError("Expected nonempty May 2026 data with unique listing IDs")

    tenancy = tenancy.loc[
        tenancy["timeframe"].eq(TENANCY_QUARTER)
        & tenancy["dwelling_type"].eq("ALL")
        & tenancy["number_of_beds"].eq("ALL")
    ].copy()
    tenancy["location_id"] = tenancy["location_id"].astype("int64")
    if tenancy.empty or tenancy["location_id"].duplicated().any():
        raise ValueError("Expected one ALL/ALL tenancy row per SA2 for the quarter")


    # Step3 54 (checks join relationship) & 57 (compares no. rows before & after join)
    # One-to-many errors now raise immediately.
    merged = listings.merge(
        tenancy,
        how="left",
        left_on="area_code",
        right_on="location_id",
        validate="many_to_one",
        indicator=True,
    )
    if len(merged) != len(listings):
        raise ValueError("Joining tenancy rows unexpectedly changed listing count")
    unmatched = int(merged["_merge"].eq("left_only").sum())
    print(f"Listings: {len(listings)}; joined rows: {len(merged)}; unmatched: {unmatched}")
    merged.drop(columns="_merge").to_csv(OUTPUT_DIR / "merged_listings.csv", index=False)

    matched = merged.loc[merged["_merge"].eq("both")].copy()
    matched["nightly_price_gap"] = matched["price"] - matched["geometric_mean_rent"] / 7

    # Mean of listing-level gaps per SA2; only areas with a rent match appear.
    by_area = (
        matched.groupby("area_code", as_index=False)
        .agg(mean_nightly_price_gap=("nightly_price_gap", "mean"))
        .sort_values("mean_nightly_price_gap")
    )
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.bar(by_area["area_code"].astype(str), by_area["mean_nightly_price_gap"])
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set(title="Mean Airbnb asking-price gap by SA2 (May 2026 vs Q2 rent)",
           xlabel="SA2 code", ylabel="Mean Airbnb nightly price minus weekly geometric mean rent / 7 ($)")
    ax.tick_params(axis="x", labelrotation=90, labelsize=6)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "difference_by_area.png", dpi=150)
    plt.close(fig)

    # Assign each SA2 to the ward containing most of its observed listings.
    # This prevents counting the same SA2's bonds twice across ward labels.
    area_ward_counts = (
        matched.groupby(["area_code", "neighbourhood"], as_index=False)
        .agg(ward_listing_count=("id", "nunique"))
        .sort_values(["area_code", "ward_listing_count", "neighbourhood"],
                     ascending=[True, False, True])
    )
    ward_for_area = area_ward_counts.drop_duplicates("area_code")[["area_code", "neighbourhood"]]
    area_counts = matched.groupby("area_code", as_index=False).agg(
        airbnb_listings=("id", "nunique"), total_bonds=("total_bonds", "first")
    )
    area_counts = area_counts.merge(ward_for_area, on="area_code", validate="one_to_one")
    by_ward = (
        area_counts.groupby("neighbourhood", as_index=False)
        .agg(airbnb_listings=("airbnb_listings", "sum"), total_bonds=("total_bonds", "sum"))
        .sort_values("neighbourhood")
    )
    by_ward.to_csv(OUTPUT_DIR / "counts_by_ward.csv", index=False)

    # These are counts of different kinds, so show them side by side, not as
    # a housing-stock ratio or a single difference.
    positions = range(len(by_ward))
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.bar([i - 0.2 for i in positions], by_ward["airbnb_listings"], width=0.4,
           label="Airbnb listings in May snapshot")
    ax.bar([i + 0.2 for i in positions], by_ward["total_bonds"], width=0.4,
           label="Total bonds in Q2 tenancy table")
    ax.set_xticks(list(positions), by_ward["neighbourhood"], rotation=70, ha="right")
    ax.set(title="Airbnb listings and tenancy bonds by assigned ward",
           xlabel="Ward", ylabel="Count")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "bnb_vs_rental_by_ward.png", dpi=150)
    plt.close(fig)
    print(f"Saved merged data, ward summary, and two graphs in {OUTPUT_DIR}/")
    print("Review SA2 boundary version and unmatched areas before drawing conclusions.")


if __name__ == "__main__":
    main()

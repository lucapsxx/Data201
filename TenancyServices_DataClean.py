import pandas as pd

#reading
INPUT= "Data201/data/QuarterlyTenency_2020_2026.csv"
OUTPUT = "Data201/data/QuarterlyTenencyCleaned.csv"
df = pd.read_csv(INPUT)

print(df.shape)

#Fixing column names
df.columns = (
    df.columns
      .str.strip()
      .str.lower()
      .str.replace(" ", "_")
)

#Cleaning dupes and missing. Dataset did not actually have any duplicates.
df["timeframe"] = pd.to_datetime(df["timeframe"], errors = "coerce")
df = df.drop_duplicates()
df = df.dropna()

#Filtering to include only 2025 oct - 2026 june
StartDate = '2025-10-01'
EndDate = '2026-06-01'
df = df[
    (df["timeframe"] >= StartDate) & 
    (df["timeframe"] <= EndDate)
]

#Dropping unecessary columns
df = df.drop(columns = {
    "active_bonds", 
    "closed_bonds", 
    "geometric_mean_rent",
    "upper_quartile_rent",
    "lower_quartile_rent",
    "log_std_dev_weekly_rent"
})

#SA2-2019 area definition ids do are within certain range of 100100 - 400016 so dropping rows outside this range
df = df[
    (df["location_id"] >= 100100) &
    (df["location_id"] <= 400016)
]

df.to_csv(OUTPUT, index = False)



import pandas as pd

# Load dataset
listings = pd.read_csv("data/airbnb_with_area_codes.csv")
tenency = pd.read_csv("data/QuarterlyTenencyCleaned.csv")

new_table = pd.merge(listings, tenency, how="left", left_on="area_code", right_on="location_id")
print(new_table)

#finding median AirBNB price in chch central
chch_central = new_table[new_table["area_code"] == 326600]
print(chch_central["price"].median())
#the median AirBNB price in chch central is $253 per night

# Find average difference between airbnb per night and rental per night
differences_table = new_table[(new_table["dwelling_type"] == "ALL") & (new_table["number_of_beds"] == "ALL")].copy()
differences_table["difference"] = differences_table["price"] - (differences_table["geometric_mean_rent"] / 7)
print(differences_table)


import matplotlib.pyplot as plt

#sorting
diff_by_area = differences_table.groupby(["area_code", "neighbourhood"])["difference"].mean().reset_index()
diff_by_area = diff_by_area.sort_values("difference") 

#plot
fig, ax = plt.subplots(figsize=(14, 6))
ax.bar(diff_by_area["area_code"].astype(str), diff_by_area["difference"])
ax.axhline(0, color="black", linewidth=0.8) 
ax.set_xlabel("Area code")
ax.set_ylabel("Avg difference (Airbnb nightly price − weekly rent/7)")
ax.set_title("Difference between Airbnb price and daily-equivalent rent, by area")
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig("difference_by_area.png", dpi=150)
plt.show()

max_row = diff_by_area.loc[diff_by_area["difference"].idxmax()]
print(max_row["neighbourhood"])

#the max difference is in papanui with an airbnb costing $522 more per night than a rental

#this creates two new columns for each different area code with the number of airbnbs which is just the count of the different names
# the other column is total bonds
area_summary = (
    differences_table
    .groupby(["area_code", "neighbourhood"])
    .agg(
        num_bnbs=("name", "nunique"),        
        total_bonds=("total_bonds", "first")  
    )
    .reset_index()
)

#this sorts all the values by their differences and finds the mean difference between all the areas within neighbourhoods
# there wouldnt be much difference between using sum or mean in this case

bnb_vs_rental = area_summary.copy()
bnb_vs_rental["differences"] = bnb_vs_rental["total_bonds"] - bnb_vs_rental["num_bnbs"]
bnb_vs_rental = bnb_vs_rental.sort_values("differences")
neighbourhood_summary = (
    bnb_vs_rental
    .groupby("neighbourhood")["differences"]
    .mean()
    .reset_index()
    .sort_values("differences")
)

#plot
fig, ax = plt.subplots(figsize=(14, 6))
ax.bar(neighbourhood_summary["neighbourhood"], neighbourhood_summary["differences"])
ax.axhline(0, color="black", linewidth=0.8)
ax.set_xlabel("Neighbourhood (Ward)")
ax.set_ylabel("Total bonds − number of Airbnb listings")
ax.set_title("Long-term rentals vs Airbnb listings by ward")
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig("bnb_vs_rental_by_ward.png", dpi=150)
plt.show()
print(bnb_vs_rental)
OUTPUT = "data/merged_listings.csv"
new_table.to_csv(OUTPUT, index = False)

#Christchurch central has the most airbnbs to rentals ratio and Spreydon has the least airbnbs to rentals ratio
#this makes sense as when people come to stay in Christchurch for breif trips, they typically stay in the city centre

print(differences_table["num_b"])
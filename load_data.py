import pandas as pd

df = pd.read_csv('/Users/debraylouis/Desktop/DATA 202 /Data set /listings.csv')
print(df.shape)


df_chch = df[df["region_parent_name"] == "Christchurch City"].copy()
print(df_chch.shape)
df_chch["month_year"] = "2026-5"

df["price"] = df["price"].replace('[\$,]', '', regex=True).astype(float)
df_chch["price"] = df_chch["price"].replace('[\$,]', '', regex=True).astype(float)

print(df["price"].dtype)
print(df["price"].head())

#4. Tout combiner proprement dans un seul résumé lisible (pratique si vous avez 96 colonnes) :
def summarize(df):
    summary = pd.DataFrame({
        "dtype": df.dtypes,
        "missing": df.isna().sum(),
        "missing_pct": (df.isna().sum() / len(df) * 100).round(1),
        "n_unique": df.nunique()
    })
    numeric_stats = df.describe().T[["min", "max", "mean", "std"]]
    summary = summary.join(numeric_stats)
    return summary

resume = summarize(df_chch)
resume


#Last week no code 

#Histogramme du prix

import matplotlib.pyplot as plt

# Histogrammes séparés


fig, axes = plt.subplots(1, 2, figsize=(12, 5))
df["price"].hist(bins=50, ax=axes[0]) # BINS 
axes[0].set_title("Distribution des prix - Nouvelle-Zélande")
axes[0].set_xlabel("Prix")

df_chch["price"].hist(bins=50, ax=axes[1])
axes[1].set_title("Distribution des prix - Christchurch")
axes[1].set_xlabel("Prix")

plt.tight_layout()
plt.show()



#Jours depuis le dernier avis

df_chch["last_review"] = pd.to_datetime(df_chch["last_review"])
df_chch["last_scraped"] = pd.to_datetime(df_chch["last_scraped"])
df_chch["days_since_last_review"] = (df_chch["last_scraped"] - df_chch["last_review"]).dt.days

plt.figure(figsize=(8, 5))
df_chch["days_since_last_review"].hist(bins=50)
plt.xlabel("Jours depuis le dernier avis")
plt.ylabel("Nombre d'annonces")
plt.title("Distribution du délai depuis le dernier avis - Christchurch")
plt.show()


#Top 10% des propriétés avec le plus d'avis (dans tout le NZ), combien à Christchurch


seuil = df["number_of_reviews"].quantile(0.90)
top10pct = df[df["number_of_reviews"] >= seuil]
print(f"Nombre total dans le top 10% (NZ) : {len(top10pct)}")

top10pct_chch = top10pct[top10pct["region_parent_name"] == "Christchurch City"]
print(f"Dont à Christchurch : {len(top10pct_chch)}")

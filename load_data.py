import matplotlib.pyplot as plt
import pandas as pd

# Load dataset
df = pd.read_csv('listings-2.csv')
print(df.shape)


# Clean price column on full dataset
df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)

# Filter for Christchurch City
df_chch = df[df['neighbourhood_group'] == 'Christchurch City'].copy()

print(df_chch.shape)

# Add month_year column
df_chch['month_year'] = '2026-5'
df_chch['last_scraped'] = pd.Timestamp.now().normalize()
# Calculate days since last review for Christchurch
df_chch['last_review'] = pd.to_datetime(df_chch['last_review'])

df_chch['days_since_last_review'] = (
    df_chch['last_scraped'] - df_chch['last_review']
).dt.days

# ==========================================
# SAVE CHRISTCHURCH DATASET TO CSV
# ==========================================
output_csv = (
    'listings_christchurch_output.csv'
)
df_chch.to_csv(output_csv, index=False)
print(f'Christchurch output CSV saved to: {output_csv}')


# 4. Summary table function
def summarize(df_in):
  summary = pd.DataFrame({
      'dtype': df_in.dtypes,
      'missing': df_in.isna().sum(),
      'missing_pct': (df_in.isna().sum() / len(df_in) * 100).round(1),
      'n_unique': df_in.nunique(),
  })
  numeric_stats = df_in.describe().T[['min', 'max', 'mean', 'std']]
  summary = summary.join(numeric_stats)
  return summary


resume = summarize(df_chch)


# Price Histograms
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
df['price'].hist(bins=50, ax=axes[0])
axes[0].set_title('Distribution des prix - Nouvelle-Zélande')
axes[0].set_xlabel('Prix')

df_chch['price'].hist(bins=50, ax=axes[1])
axes[1].set_title('Distribution des prix - Christchurch')
axes[1].set_xlabel('Prix')

plt.tight_layout()
plt.show()

# Histogram: Days since last review
plt.figure(figsize=(8, 5))
df_chch['days_since_last_review'].hist(bins=50)
plt.xlabel('Jours depuis le dernier avis')
plt.ylabel("Nombre d'annonces")
plt.title('Distribution du délai depuis le dernier avis - Christchurch')
plt.show()

# Top 10% most reviewed properties in NZ
seuil = df['number_of_reviews'].quantile(0.90)
top10pct = df[df['number_of_reviews'] >= seuil]
print(f'Nombre total dans le top 10% (NZ) : {len(top10pct)}')

top10pct_chch = top10pct[top10pct['region_parent_name'] == 'Christchurch City']
print(f'Dont à Christchurch : {len(top10pct_chch)}')
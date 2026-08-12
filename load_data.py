import pandas as pd

df = pd.read_csv("data/listings_2025-10.csv")
print(df.shape)
print(df.columns.tolist())
df.head()




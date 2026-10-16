import pandas as pd

# Load dataset
df1 = pd.read_csv("data/julyairbnb.csv")
df2 = pd.read_csv("data/augustairbnb.csv")

def merge_months(df1, df2):
    df = pd.concat([df1, df2], ignore_index=True)

    return df

def merge_airbnb(old, new):
    df = pd.concat([old, new], ignore_index=True)
    df.to_csv("data/airbnbcleaned.csv", index=False)
    return df

new = merge_months(df1, df2)
old = pd.read_csv("data/airbnbcleaned.csv")

merge_airbnb(old, new)


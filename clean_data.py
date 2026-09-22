import pandas as pd

df = pd.read_csv("Data Set/saudi_influenza_who_2015_2026.csv")

# remove cols with no data at all
columns_all_null = []
for column in df.columns:
    if df[column].isnull().all():
        columns_all_null.append(column)
df.drop(columns=columns_all_null, inplace=True)
print("dropped empty columns:", columns_all_null)

df["ISO_WEEKSTARTDATE"] = pd.to_datetime(df["ISO_WEEKSTARTDATE"])
df.sort_values("ISO_WEEKSTARTDATE", inplace=True)
df.reset_index(drop=True, inplace=True)

df["SPEC_PROCESSED_NB"] = df["SPEC_PROCESSED_NB"].fillna(df["SPEC_RECEIVED_NB"])

non_virus_columns = ["COUNTRY_AREA_TERRITORY", "ISO_YEAR", "ISO_WEEK", "ISO_WEEKSTARTDATE"]
virus_count_columns = []
for column in df.columns:
    if column not in non_virus_columns:
        virus_count_columns.append(column)

df[virus_count_columns] = df[virus_count_columns].fillna(0).astype(int)

print("rows:", len(df), " columns:", df.shape[1])
print("missing values left:", df.isna().sum().sum())

#save
df.to_csv("Data Set/saudi_influenza_who_2015_2026_cleaned.csv", index=False)

import pandas as pd

flu = pd.read_csv("Data Set/saudi_influenza_who_2015_2026_cleaned.csv",
                  parse_dates=["ISO_WEEKSTARTDATE"])
weather = pd.read_csv("Data Set/saudi_weather_weekly.csv",
                      parse_dates=["ISO_WEEKSTARTDATE"])

flu = flu[flu["ISO_YEAR"] >= 2017]
flu = flu.sort_values("ISO_WEEKSTARTDATE").reset_index(drop=True)

weeks = pd.date_range(flu["ISO_WEEKSTARTDATE"].min(), flu["ISO_WEEKSTARTDATE"].max(), freq="7D")
flu = flu.set_index("ISO_WEEKSTARTDATE").reindex(weeks)
flu.index.name = "ISO_WEEKSTARTDATE"
print("missing weeks:", int(flu["INF_ALL"].isna().sum()))

counts = ["INF_ALL", "SPEC_PROCESSED_NB"]
flu[counts] = flu[counts].interpolate().round().astype(int)
flu = flu.reset_index()

df = flu.merge(weather, on="ISO_WEEKSTARTDATE", how="left", validate="one_to_one")
assert df["temperature_C"].notna().all(), "some weeks have no weather data"

df["ISO_WEEK"] = df["ISO_WEEKSTARTDATE"].dt.isocalendar().week
df["positivity_rate"] = df["INF_ALL"] / df["SPEC_PROCESSED_NB"].replace(0, pd.NA)
df["positivity_rate"] = df["positivity_rate"].fillna(0)

df = df[["ISO_WEEKSTARTDATE", "ISO_WEEK", "INF_ALL", "SPEC_PROCESSED_NB",
         "positivity_rate", "temperature_C", "humidity_pct", "wind_speed_ms"]]

split = int(len(df) * 0.8)
train = df.iloc[:split]
test = df.iloc[split:]

train.to_csv("Data Set/flu_train.csv", index=False)
test.to_csv("Data Set/flu_test.csv", index=False)
print("columns:", df.shape[1])
print("train:", len(train), "weeks")
print("test:", len(test), "weeks")

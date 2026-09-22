import requests
import pandas as pd
import time

cities = {
    "Riyadh": (24.7136, 46.6753),
    "Jeddah": (21.4858, 39.1925),
    "Dammam": (26.4207, 50.0888),
    "Abha": (18.2164, 42.5053),
    "Tabuk": (28.3998, 36.5715),
    "Hail": (27.5114, 41.7208),
    "Najran": (17.4924, 44.1277),
    "Jazan": (16.8892, 42.5611),
}

frames = []

for name, (lat, lon) in cities.items():
    print(name)
    r = requests.get(
        "https://archive-api.open-meteo.com/v1/archive",
        params={
            "latitude": lat, "longitude": lon,
            "start_date": "2017-01-02", "end_date": "2026-07-19",
            "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            "wind_speed_unit": "ms", "timezone": "auto",
        },
        timeout=120
    )

    if r.status_code != 200:
        print("failed", name, r.status_code)
        continue

    j = r.json()["hourly"]
    df = pd.DataFrame(j)
    df["time"] = pd.to_datetime(df["time"])
    df["city"] = name
    df = df.rename(columns={
        "temperature_2m": "temp",
        "relative_humidity_2m": "hum",
        "wind_speed_10m": "wind"
    })
    frames.append(df)
    time.sleep(1)

data = pd.concat(frames, ignore_index=True).dropna()

data["yr"] = data["time"].dt.isocalendar().year
data["wk"] = data["time"].dt.isocalendar().week

g1 = data.groupby(["yr", "wk", "city"])[["temp", "hum", "wind"]].mean().reset_index()
g2 = g1.groupby(["yr", "wk"])[["temp", "hum", "wind"]].mean().reset_index()

g2["date"] = pd.to_datetime(
    g2["yr"].astype(str) + "-" + g2["wk"].astype(str) + "-1", format="%G-%V-%u"
)

g2 = g2.sort_values("date")
g2 = g2.rename(columns={
    "date": "ISO_WEEKSTARTDATE",
    "temp": "temperature_C",
    "hum": "humidity_pct",
    "wind": "wind_speed_ms",
})

out = g2[["ISO_WEEKSTARTDATE", "temperature_C", "humidity_pct", "wind_speed_ms"]]
out.to_csv("Data Set/saudi_weather_weekly.csv", index=False)

print("cities:", data["city"].nunique(), "of", len(cities))
print("saved", len(out), "weeks")

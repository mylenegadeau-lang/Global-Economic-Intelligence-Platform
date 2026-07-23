import requests
import pandas as pd


url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=20000"

#Send the requests
response = requests.get(url)

#convert Json
if response.status_code == 200:
    data = response.json()
    print(f"Total records returned: {data[0]['total']}")
    records = []
    for item in data[1]:
        val = item.get("value")
        gdp_billions = (val / 1e9) if val is not None else None

        country_code = item.get("countryiso3code") or item.get("country", {}).get("id", "")
        records.append({"country": item["country"]["value"], "country_code": country_code, "Year": int(item['date']), "GDP_Billions": gdp_billions})
    df = pd.DataFrame(records)
    df.to_csv("data/gdp_data.csv", index=False)
    print("Succesfully saved all records to data/gdp_data.csv!")


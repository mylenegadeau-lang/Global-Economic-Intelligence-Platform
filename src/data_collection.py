import requests
import pandas as pd


url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=5000"

#Send the requests
response = requests.get(url)
print(response.status_code)

#convert Json
data = response.json()

#Json file exploration
print(type(data))
print(len(data))

#view the Metadata
print(data[0])

#view one record
print(data[1][0])

#creating an empty list
records = []

#loop through the data
for item in data[1]:
    records.append({"country": item["country"]["value"], "country code": item["countryiso3code"], "Year": item["date"], "GDP": item["value"]})

#convert to a dataframe
df = pd.DataFrame(records)

#inspect the data
print(df.head()) 
print(df.info())

#Summary statitics
print(df.describe())

#Looking for missing values
print(df.isnull().sum())

#saving the data
df.to_csv('data/gdp_data.csv', index=False)
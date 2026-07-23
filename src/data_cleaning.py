import pandas as pd
df = pd.read_csv("data/gdp_data.csv")

#Inspect data
print("--- Head ---")
print(df.head())
print("\n--- Info ---")
print(df.info())
print(f"\nShape: {df.shape}")

#Check Missing Values
print("\n--- Missing Values Before Cleaning ---")
print(df.isnull().sum())

#Remove Missing GDP Values
df = df.dropna(subset=["GDP_Billions"])

#Convert Year to Numeric
df["Year"] = pd.to_numeric(df["Year"])

#Check Duplicates
print(f"\nDuplicates found: {df.duplicated().sum()}")
df = df.drop_duplicates()

df_countries = df[df["country_code"].notnull() & (df["country_code"] != "")]

#Find Top 10 Countries by GDP in the latest year
latest_year = df["Year"].max()
latest_df = df_countries[df_countries["Year"] == latest_year]

top10 = latest_df.nlargest(10, "GDP_Billions")
print(f"\n--- Top 10 Economies in {int(latest_year)} ---")
print(top10[["country", "country_code", "GDP_Billions"]])

#Save cleaned dataset
df.to_csv("data/gdp_cleaned.csv", index=False)
print("\nSuccessfully saved cleaned data to data/gdp_cleaned.csv!")


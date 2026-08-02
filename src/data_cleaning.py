import pandas as pd
import country_converter as coco

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

# 4. Filter out rows with invalid or missing country codes
df = df[df["country_code"].notnull() & (df["country_code"].astype(str).str.strip() != "")]

# Remove ", the" from the end of country
def clean_country_names(name):
    if pd.isna(name):
        return name
    name = name.strip()
    if name.endswith(", The"):
        base_name = name[:-5].strip()
        return f"The {base_name}"
    return name
df['country'] = df['country'].apply(clean_country_names)

cc = coco.CountryConverter()
df["Region"] = cc.convert(names=df["country"].tolist(), to="continent", not_found="Global / Other")

# Function to classify income based on gdp value
def get_income_category(gdp):
    if pd.isna(gdp):
        return "Unknown"
    elif gdp > 500:
        return "High Income"
    elif gdp >= 50:
        return "Middle Income"
    else:
        return "Low Income"

df["Income_Group"] = df["GDP_Billions"].apply(get_income_category)

# Calculate YoY GDP growth (%) per country
df = df.sort_values(["country", "Year"])
df["GDP_Growth"] = df.groupby("country")["GDP_Billions"].pct_change() * 100


latest_years = df.groupby("country")["Year"].transform(max)
latest_df = df[df["Year"] == latest_years]


#Save cleaned dataset
df.to_csv("data/gdp_cleaned.csv", index=False)
print("\nSuccessfully saved cleaned data to data/gdp_cleaned.csv!")


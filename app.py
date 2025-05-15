import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Thali Dataset Analysis - Attero Assessment")

FILE_PATH = "Interview_Dataset.xlsx"  # Ensure this file is in your project folder

@st.cache_resource
def load_excel(file_path):
    return pd.ExcelFile(file_path)

def load_sheet_dynamic(xls, sheet_name):
    # Preview top 20 rows without header to find actual header row
    preview = xls.parse(sheet_name, nrows=20, header=None)
    start_row = preview[preview.iloc[:, 0].astype(str).str.contains("sr no", case=False, na=False)].index[0]
    df = xls.parse(sheet_name, skiprows=start_row)
    return df

try:
    xls = load_excel(FILE_PATH)

    south = load_sheet_dynamic(xls, "South Indian Thali")
    gujarati = load_sheet_dynamic(xls, "Gujarati Thali")
    north = load_sheet_dynamic(xls, "North Indian Thali")

    # Add region labels
    south["region"] = "South"
    gujarati["region"] = "Gujarati"
    north["region"] = "North"

    # Combine all into one dataframe
    df = pd.concat([south, gujarati, north], ignore_index=True)

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w\s]", "", regex=True)
    )

    # Rename relevant columns (adjust names if your columns differ)
    df.rename(columns={
        "thali_item": "dish_name",
        "ingredients_spicesveggies": "ingredients",
        "weight_in_grams": "weight"
    }, inplace=True)

    # Validate required columns
    required_columns = {"dish_name", "ingredients", "weight"}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        st.error(f"Missing required columns: {missing}")
    else:
        # Clean data
        df.dropna(subset=["ingredients", "weight"], inplace=True)
        df["ingredients"] = df["ingredients"].astype(str).str.strip().str.lower()

        # 1. Unique Dishes per Region
        st.subheader("1. Unique Dishes per Region")
        dish_count = df.groupby("region")["dish_name"].nunique().reset_index(name="unique_dishes")
        fig1 = px.bar(dish_count, x="region", y="unique_dishes", title="Unique Dishes per Region")
        st.plotly_chart(fig1, use_container_width=True)

        # 2. Average Ingredients per Dish
        st.subheader("2. Average Ingredients per Dish (Region-wise)")
        avg_ings = df.groupby(["region", "dish_name"]).size().groupby("region").mean().reset_index(name="avg_ingredients")
        fig2 = px.bar(avg_ings, x="region", y="avg_ingredients", title="Avg Ingredients per Dish")
        st.plotly_chart(fig2, use_container_width=True)

        # 3. Top 4 Most Common Ingredients
        st.subheader("3. Top 4 Most Common Ingredients")
        top_4 = df["ingredients"].value_counts().head(4).reset_index()
        top_4.columns = ["ingredient", "count"]
        fig3 = px.bar(top_4, x="ingredient", y="count", title="Top 4 Most Common Ingredients")
        st.plotly_chart(fig3, use_container_width=True)

        # 4. Spice vs Non-Spice Ratio
        st.subheader("4. Spice vs Non-Spice Ingredient Ratio")
        spices = ['turmeric', 'chili', 'mustard', 'jeera', 'hing', 'garam masala', 'coriander', 'clove', 'cinnamon']
        df["is_spice"] = df["ingredients"].apply(lambda x: 1 if any(s in x for s in spices) else 0)
        spice_ratio = df.groupby("region")["is_spice"].mean().reset_index(name="spice_ratio")
        fig4 = px.bar(spice_ratio, x="region", y="spice_ratio", title="Spice Ratio by Region")
        st.plotly_chart(fig4, use_container_width=True)

        st.success("✅ Analysis complete! Ready for submission.")

except FileNotFoundError:
    st.error(f"❌ Excel file '{FILE_PATH}' not found. Please place it in the project folder.")
except Exception as e:
    st.error(f"❌ Error occurred: {e}")

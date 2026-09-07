import streamlit as st
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# ShopSphere E-commerce Analytics Dashboard
# --------------------------------------------------

st.set_page_config(
    page_title="ShopSphere Analytics",
    page_icon="🛒",
    layout="wide"
)

# --------------------------------------------------
# Load processed dataset
# --------------------------------------------------

DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "ShopSphere_Final_Processed.csv"
)

if not DATA_FILE.exists():
    st.error(
        "Processed dataset not found. "
        "Please make sure ShopSphere_Final_Processed.csv "
        "is available inside the data folder."
    )
    st.stop()

df = pd.read_csv(DATA_FILE)

# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("🛒 ShopSphere E-commerce Analytics Dashboard")
st.caption(
    "E-commerce KPI analysis using Python, Pandas, Looker Studio "
    "and Streamlit"
)

# --------------------------------------------------
# Sidebar Filters
# --------------------------------------------------

st.sidebar.header("Filters")

if "category" in df.columns:
    categories = sorted(df["category"].dropna().unique().tolist())
    selected_categories = st.sidebar.multiselect(
        "Category",
        categories,
        default=categories
    )
    filtered_df = df[df["category"].isin(selected_categories)].copy()

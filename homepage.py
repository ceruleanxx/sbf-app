
import streamlit as st
import pandas as pd
import importlib

from lib.initialize import load_data_by_sheet


# Set Streamlit to wide layout, this must be called at the top level before any other Streamlit function
st.set_page_config(layout="wide")

sheet_data = load_data_by_sheet()
sheet_names = list(sheet_data.keys())

# Sidebar nav
selected_exercise = st.sidebar.selectbox("📄 Select Exercise", sheet_names)

# Filter town list from selected sheet
df = sheet_data[selected_exercise]

# Make sure Town column exists
available_towns = sorted(df['Town'].dropna().unique())

# Map town names to module names
town_pages = {
    "Bishan"        : "bishan",
    "Choa Chu Kang" : "choachukang",
    "Geylang"       : "geylang",
    "Ang Mo Kio"    : "angmokio",
    "Toa Payoh"     : "toa_payoh",
    "Queenstown"    : "queenstown",
    "Kallang/Whampoa" : "kallang",
    "Woodlands"     : "woodlands"
}

# Filter towns that have a module
filtered_towns = [town for town in available_towns if town in town_pages]

# Town selector
selected_town = st.sidebar.selectbox("🏙️ Select Town", filtered_towns)

# Dynamically import and run the corresponding module
module_name = f"town.{town_pages[selected_town]}"
module = importlib.import_module(module_name)


df_final = df[df['Town'] == selected_town]
module.app(df_final, selected_town)






    


import streamlit as st
import importlib
from PIL import Image

from lib.initialize import load_data_by_sheet


import os
current_dir = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(current_dir, "assets", "template.xlsx")
compiled_data_path = os.path.join(current_dir, "assets", "compiled_july_2025.xlsx")
image_path = os.path.join(current_dir, "assets", "bmc_qr.png")

# Set Streamlit to wide layout, this must be called at the top level before any other Streamlit function
st.set_page_config(layout="wide")

left_col, right_col = st.columns([5,5])

with left_col:
    st.title("Welcome! :sunglasses:")
    st.info("Step 1: To use the app, download the template below and fill in everything from Col A to Q. Please follow the sample data already given.")
    st.info("Step 2: Then upload it on the right start to start your analysis!")

    with open(template_path, "rb") as file:
        st.download_button(
            label="📥 Download Excel Template",
            data=file,
            file_name="template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.success("You may also feel free to download the one I have already compiled.")
    with open(compiled_data_path, "rb") as file:
        st.download_button(
            label="📥 Download July 2025",
            data=file,
            file_name="sbf_july_2025.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
        
with right_col:
    uploaded_file = st.file_uploader("📄 Upload Data File", type=["xlsx"])

    if uploaded_file:
        st.success("Did you find it helpful? Consider buying me a cup of coffee: http://coff.ee/ceruleanxx")
        image = Image.open(image_path)
        st.image(image, width=200)

st.markdown("---") # Separator

if uploaded_file:
    sheet_data = load_data_by_sheet(uploaded_file)
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

    # Feedback
    st.sidebar.markdown("💬 [Submit Feedback](https://form.typeform.com/to/fUV6KBRZ)")


    






    

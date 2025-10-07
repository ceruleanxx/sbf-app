
import streamlit as st
from PIL import Image


st.cache_data.clear()  # Clear cache on app rerun
st.cache_resource.clear()  # Clear resource cache on app rerun
st.set_page_config(page_title="SBF Analyzer", page_icon="🏘️")
st.markdown(
    """
    <meta property="og:title" content="SBF Analyzer" />
    <meta property="og:description" content="Helping you make informed decisions one plot at a time!" />
    <meta property="og:image" content="https://github.com/ceruleanxx/sbf-app/raw/master/assets/thumbnail.jpg" />
    <meta property="og:url" content="https://cerulean-sbf-app.streamlit.app/" />
    """,
    unsafe_allow_html=True
)

# Set path for assets and files
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(current_dir, "assets", "template.xlsx")
compiled_data_path = os.path.join(current_dir, "assets", "compiled_july_2025.xlsx")
application_rates_path = os.path.join(current_dir, "assets", "application_rates.xlsx")
image_path = os.path.join(current_dir, "assets", "bmc_qr.png")


# Import usable modules
from lib.initialize import load_data_by_sheet
from lib.modules import appl_rate_bar
import town.app as town_module



# Set Streamlit to wide layout, this must be called at the top level before any other Streamlit function
st.set_page_config(layout="wide")


# Re-usable components
def buy_me_coffee():
    st.success("If you found this useful, please consider buying me a cup of coffee: http://coff.ee/ceruleanxx")
    image = Image.open(image_path)
    st.image(image, width=200)



#======================================================
# START OF THE APPLICATION
#======================================================
left_col, right_col = st.columns([5,5])

# Side bar irregardless of file upload
page = st.sidebar.radio("🧭 Navigation Pane",["Analysis by Town", "Past Application Rates"])
if page == "Past Application Rates":
    st.markdown("---") # Separator
    appl_rate_bar(application_rates_path)
    

with left_col:
    st.title("Welcome! :sunglasses:")
    st.info("Step 1: Download the template below and fill in everything from Col A to Q. You may follow the sample data already given.")
    
    with open(template_path, "rb") as file:
        st.download_button(
            label="📥 Download Excel Template",
            data=file,
            file_name="template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.info("Step 2: Then upload it below to start your analysis!")
    uploaded_file = st.file_uploader("📄 Upload Data File", type=["xlsx"])

        
with right_col:
    st.title("July 2025 SBF Compiled")
    st.success("You may also download the one I have already compiled.")
    with open(compiled_data_path, "rb") as file:
        st.download_button(
            label="📥 Download July 2025 SBF",
            data=file,
            file_name="sbf_july_2025.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    if uploaded_file or page == "Past Application Rates":
        buy_me_coffee()

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

    # Filter towns that have a module
    filtered_towns = df['Town'].unique().tolist()

    # Town selector
    selected_town = st.sidebar.selectbox("🏙️ Select Town", filtered_towns)

    # Pull the corresponding town
    df_final = df[df['Town'] == selected_town]
    town_module.app(df_final, selected_town)


# Sidebar components not affected by file upload
# Feedback

st.sidebar.markdown("💬 [Submit Feedback](https://form.typeform.com/to/fUV6KBRZ)")


    






    

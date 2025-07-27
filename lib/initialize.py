
import streamlit as st
import pandas as pd


@st.cache_data

def load_data_by_sheet(uploaded_file):
    
    data_by_sheet = pd.DataFrame()

    if uploaded_file is not None:
        xls = pd.ExcelFile(uploaded_file)
        sheet_names = xls.sheet_names

        # Return all sheets as a dict of DataFrames
        data_by_sheet = {sheet: xls.parse(sheet) for sheet in sheet_names}

    return data_by_sheet





import streamlit as st
import pandas as pd


@st.cache_data
def load_data_by_sheet():
    xls = pd.ExcelFile(r'SBF_EXERCISES_DATA_MASTER.xlsx')
    sheet_names = xls.sheet_names

    # Return all sheets as a dict of DataFrames
    data_by_sheet = {sheet: xls.parse(sheet) for sheet in sheet_names}
    return data_by_sheet


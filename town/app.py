import streamlit as st
import pandas as pd
from datetime import date

import lib.modules as mod


def app(df, selection):
    try:
        # Only take the projects that we want to compare
        df['Chinese'] = df['Chinese'].fillna(0)
        df['Malay'] = df['Malay'].fillna(0)
        df['Indian/Oth'] = df['Indian/Oth'].fillna(0)
        df['Probable Completion Date'] = pd.to_datetime(df['Probable Completion Date'])

        # Only take the rows we want to plot
        df = df[(df['Plot Graph'] == 'Y')] #& (df['Chinese'] > 0)]   
        df['Normalized_Floor'] = df['Floor'] / df['Highest Floor']
        st.title(selection)

        print(df.dtypes)
    
    except Exception as e:
        st.error(e)


    # Simulate centered layout 2 | 6 | 2 columns
    left_col, right_col = st.columns([4,6])

    with left_col:
        # Date selection (stored in session state)
        st.session_state['availability_date'] = st.date_input(
            "Flat Available Before", 
            value=st.session_state.get("availability_date", date.today())
        )
        room_options = [4, 5]
        st.session_state['room_type'] = st.radio("Room Type",
                                                 options=room_options,
                                                 index=room_options.index(st.session_state.get("room_type",4))
        )
        
        mod.pie_chart(df)

    with right_col:
        mod.unit_count_by_room_type(df)
        mod.project_summary(df)
  
    st.markdown("---") # Separator

    with st.container():
        mod.stack_projs_available(df)
        mod.unit_floor_distribution_4rm(df)
        mod.unit_floor_distribution_5rm(df)


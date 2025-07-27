# town/kallang.py

import streamlit as st
import lib.modules as mod
from lib.town_template import render_town_page

def app(df, selection):
    render_town_page(df, selection, mod)

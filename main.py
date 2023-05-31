import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(
    layout="wide", page_title="Flora Visualization", page_icon=":world_map:️"
)

st.title("Flora Visualization")

# HOME PAGE

"## Start Exploring"
"""
- `Flora`: You will be able to view the data from the Flora database. You can apply filters by specifying only the fields of interest. 
    After selecting the samples, they will be displayed on the map along with relevant information obtained from the database. 
    This information may include the species present in that location, the lithology, or the natural park to which the sample belongs, among others. 
    Additionally, any images associated with the sample will also be displayed.     

"""

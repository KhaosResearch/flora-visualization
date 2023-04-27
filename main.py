import altair as alt
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static

st.set_page_config(
    layout="wide", page_title="Greensenti Visualization", page_icon=":world_map:️"
)

st.title("Greensenti Visualization")

# HOME PAGE

"## Start Exploring"
"""
Currently there are three different display pages from different information sources:

- `Flora`: You will be able to view the data from the Flora database. You can choose to display all samples or apply filters by specifying 
    only the fields of interest. After selecting the samples, they will be displayed on the map along with relevant information obtained from the database. 
    This information may include the species present in that location, the lithology, or the Natural Park to which the sample belongs, among others. 
    Additionally, any images associated with the sample will also be displayed.

- `Genomic`: The genomics data will be located on the map. It can be filtered by date range. 

- `Soil`: Soil data will be located on the map. For each sample a time series will be shown for each index, specifying for each point whether that data pertains
 to vegetation, clouds or buildings. A table is also shown with data pertaining to that sample such as humidity, percentage of organic matter or ph, among others.
            

"""

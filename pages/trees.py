import geopandas as gpd
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static

from utils import generate_map, filter_by_region

# Set the page configuration
st.set_page_config(layout="wide")
st.title("Trees in UMA Campus")

trees_map = generate_map([36.71485, -4.49663], 14)

"## Trees in UMA Campus"
"""
Discover the tree distribution across the University of Malaga campus, including Teatinos, Extension of Teatinos, and El Ejido. 
The data, collected in 2019, offers additional metadata on each tree. You can access the raw data in multiple formats from 
https://khaos.uma.es/green-senti/opendata.
"""

region_radio = st.sidebar.radio(
    "Select the region to visualize",
    ('Ejido', 'Teatinos', 'Teatinos extension'))

if region_radio == 'Ejido':
    path = './data/ejido.geojson'
elif region_radio == 'Teatinos':
    path = './data/teatinos.geojson'
else:
    path = './data/extension_teatinos.geojson'

gdf = gpd.read_file('./data/arboles-greensenti-2019-v01.geojson')
gdf = gdf.to_crs(crs=4326)


df_filter = filter_by_region(gdf, path)
df_region = df_filter.copy()
df_region["LATITUDE"] = df_region["geometry"].y
df_region["LONGITUDE"] = df_region["geometry"].x
df_region = df_region.drop(['FID_1', 'geometry'], axis=1)

location=[]
for _, fila in df_region.iterrows():
    location.append([fila["LATITUDE"], fila["LONGITUDE"]])
    html = pd.DataFrame(fila).to_html(header=False)
    iframe = folium.IFrame(html, width=250, height=220)
    popup = folium.Popup(iframe)
    marker = folium.Marker(location=[fila['LATITUDE'], fila['LONGITUDE']], 
                           popup=(popup),
                           tooltip=fila['Origen']).add_to(trees_map)
    trees_map.add_child(marker)
                        


trees_map.fit_bounds(location)
folium_static(trees_map, height=700, width=1300)
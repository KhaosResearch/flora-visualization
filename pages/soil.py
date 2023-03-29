
import altair as alt
from minio_client import minio_connection
import folium
import pandas as pd
import streamlit as st
import json
import datetime
from streamlit_folium import folium_static
from mongo_client import get_collection_object
from utils import generate_map



# Set the page configuration
st.set_page_config(layout="wide")



collection = get_collection_object()

cliente = minio_connection()


st.title("Soil map")



soil_map = generate_map()
df_vegetation = pd.read_csv('./data/vegetationindex.csv', delimiter=',')
df_info = pd.read_csv('./data/results.csv', delimiter=',')
print(df_info.head())

df_vegetation["DATE"] = [datetime.datetime.strptime(str(x), '%Y%m%d') for x in df_vegetation["DATE"]  ]
uniques_samples = df_vegetation["SAMPLE"].unique()

# aa = df_vegetation.melt('DATE', var_name='NDVI', value_name='bvalue')
# print(aa)

dff = pd.read_csv('/home/irene/Working_dir/greensenti-visualization/pp.csv', delimiter=',')

gh =['vegetation','cloud', 'built']
gh
n = [datetime.datetime.strptime(str(20190203), '%Y%m%d'), datetime.datetime.strptime(str(20190203), '%Y%m%d'),datetime.datetime.strptime(str(20190203), '%Y%m%d')]
for i in range(len(uniques_samples)):
    sample = df_vegetation.loc[df_vegetation['SAMPLE'] == uniques_samples[i]]
    sample = sample.reset_index(drop=True)

    #Transform the df to plot multiple columns in the Y axis
    sample_band_info = sample.melt('DATE', value_vars= ['NDVI','SLAVI','GVMI','NDWI','BSI','NPCRI'], var_name='band', value_name='bvalue')
    sample_band_info['class'] = pd.concat([sample['CLASS']]*len(['NDVI','SLAVI','GVMI','NDWI','BSI','NPCRI']), ignore_index=True)

    #g= sample_band_info.append([{"class": v} for v in gh], ignore_index=True)


    vega_chart = alt.Chart(dff).mark_line(point=True).encode(

    alt.X('DATE:T', axis=alt.Axis(format="%Y-%m-%d")),
    alt.Y('bvalue'),
    alt.Color('band'),
    alt.Shape('class', legend=alt.Legend(values=gh, symbolType=['cross', 'circle', 'square'])),
    tooltip = [alt.Tooltip('band'),
                alt.Tooltip('bvalue'),
                alt.Tooltip('class'),
                alt.Tooltip('DATE'),
              ]
    ).interactive().properties(
    width=350,
    height=300,
    title= uniques_samples[i] 
).configure_axis(
    labelFontSize=10,
    titleFontSize=10
).configure_point(
    size=100
)
    
    vega_chart = folium.VegaLite(vega_chart, height= 350, width=500)
    popup = folium.Popup().add_child(vega_chart)
    marker = folium.Marker(
            [sample["LONGITUDE"][0], sample["LATITUDE"][0]],
            popup= (popup),
            tooltip= uniques_samples[i] 
        ).add_to(soil_map)
    soil_map.add_child(marker)

# for i in range(len(df_vegetation)):
#     print("dd",type(df_vegetation["DATE"][i])) 
#     print("ss",type(selected_date))
#     if df_vegetation["DATE"][i] == selected_date:
#         vega_chart = folium.VegaLite(vega_chart)
#         popup = folium.Popup().add_child(vega_chart)
#         marker = folium.Marker(
#             [df_vegetation["LONGITUDE"][i],df_vegetation["LATITUDE"][i]],
#             popup= (popup),
#             tooltip= df_vegetation["SAMPLE"][i] +" - " + str(selected_date)
#         ).add_to(soil_map)
#         soil_map.add_child(marker)








# Add the map to the Streamlit app
folium_static(soil_map, height=500, width=1300)

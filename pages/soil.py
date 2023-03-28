

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


start_date = st.sidebar.date_input(
    "Intruduce fecha de comienzo",
    value=pd.to_datetime("2019-01-01", format="%Y-%m-%d"),
)

end_date = st.sidebar.date_input("Intruduce fecha final")
end_date = end_date + datetime.timedelta(days=1)
end_date = end_date.strftime("%Y/%m/%dT00:00:00.000Z").replace("/", "-")
start_date = (start_date.strftime("%Y/%m/%d") + "T00:00:00.000Z").replace("/", "-")

soil_map = generate_map()
df_vegetation = pd.read_csv('./data/vegetationindex.csv', delimiter=',')

df_vegetation["DATE"] = [datetime.datetime.strptime(str(x), '%Y%m%d').date() for x in df_vegetation["DATE"]  ]

# for x in df_vegetation:
#     print(x)
# dateRange = [df_vegetation.iloc[x] for x in range(len(df_vegetation)) if df_vegetation["DATE"][x] >= start_date and df_vegetation["DATE"][x] <= end_date ]

#dateRange
json_vegetation  = json.loads(df_vegetation.to_json(orient = 'records', date_format='iso'))

for veg in json_vegetation: 


    if veg["DATE"]>= start_date and veg["DATE"] <= end_date:
        print(type(veg["DATE"]))
        marker = folium.Marker(
            [veg["LONGITUDE"],veg["LATITUDE"]],
            popup= veg["SAMPLE"],
            tooltip= veg["SAMPLE"] +" - " + str(datetime.datetime.fromisoformat(veg["DATE"]).date())
        ).add_to(soil_map)
        soil_map.add_child(marker)








# Add the map to the Streamlit app
folium_static(soil_map, height=500, width=1300)

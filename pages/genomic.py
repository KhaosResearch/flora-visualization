import datetime

import folium
import streamlit as st
from streamlit_folium import folium_static

from config import settings
from mongo_client import get_collection_object
from utils import generate_map

# Set the page configuration
st.set_page_config(layout="wide")

collection = get_collection_object(
    settings.MONGO_DB_GENOM, settings.MONGO_COLLECTION_GENOM
)


st.title("Genomics map")
query_list = []
genom_map = generate_map([37.3522, -4.64363], 8)


dates_unique = collection.distinct("created_at")
dates_unique.sort()
min_date = datetime.datetime.strptime((dates_unique[0].split("T"))[0], "%Y-%m-%d")
max_date = datetime.date.today()
range_date = st.sidebar.date_input("Date range", (min_date, max_date))

try:
    start_date = (range_date[0].strftime("%Y/%m/%d") + "T00:00:00.000Z").replace(
        "/", "-"
    )
    end_date = range_date[1].strftime("%Y/%m/%dT23:59:59.000Z").replace("/", "-")
    query_list.append({"$or": [{"created_at": {"$gte": start_date, "$lt": end_date}}]})
except:
    st.sidebar.warning("Incomplete range")


try:
    print("Query list", query_list)
    # If the query list is not empty, use it to find matching documents in the MongoDB collection
    if len(query_list) > 0:
        cursor = collection.find({"$and": query_list})
    # If the query list is empty, find all documents in the collection
    else:
        cursor = collection.find()
except Exception as e:
    print(e)


# For each matching document, create a marker on the map with a popup containing the document's images


for document in cursor:
    # There are some sample without location
    if document["Latitude"] and document["Longitude"]:
        marker = folium.Marker(
            [document["Latitude"], document["Longitude"]],
            popup=document["_id"],
            tooltip=document["_id"],
        ).add_to(genom_map)
        genom_map.add_child(marker)


folium_static(genom_map, height=700, width=1300)

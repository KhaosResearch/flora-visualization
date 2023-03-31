import base64
import datetime

from minio_client import minio_connection
import folium
import pandas as pd
import streamlit as st
from config import settings
from utils import generate_map
from streamlit_folium import folium_static
from mongo_client import get_collection_object

# Set the page configuration
st.set_page_config(layout="wide")

# Function to update the query list based on the selected variety of crop
def variety_selection(crop_list_variety, crop):
    """
    This function receives a list of dictionaries (each one belongs to a selected variety), it also receives the crop in order to filter the Crops by the selected variety.
    :param crop_list_variety: Variety list dict (list[dict[str, any]]).
    :param crop: Crop name (string).
    """
    # Find the index of the selected crop in the query list
    for i in range(len(menu_query)):
        if "Crop" in menu_query[i].keys() and menu_query[i]["Crop"]["$regex"] == crop:
            index = i
    # Remove the query for the selected crop
    query_list[1]["$or"].pop(index)
    # Add the queries for the selected crop varieties
    for i in range(len(crop_list_variety)):
        query_list[1]["$or"].append(crop_list_variety[i])
    # Remove the query for the crop variety if it was previously added
    query_list.pop(2)



collection = get_collection_object(settings.MONGO_DATABASE, settings.MONGO_COLLECTION)

client = minio_connection()


st.title("Mapa de ubicación de cultivos")

crop_map = generate_map([36.71485, -4.49663], 15)


# Initialize the query list with a query for the selected dates
query_list = []
st.sidebar.title("Filtrar cultivos")
start_date = st.sidebar.date_input(
    "Intruduce fecha de comienzo",
    value=pd.to_datetime("01-01-2023", format="%d-%m-%Y"),
)
end_date = st.sidebar.date_input("Intruduce fecha final")
end_date = end_date + datetime.timedelta(days=1)
end_date = end_date.strftime("%Y/%m/%dT00:00:00.000Z").replace("/", "-")
start_date = (start_date.strftime("%Y/%m/%d") + "T00:00:00.000Z").replace("/", "-")

print("hkkk", type(start_date))
query_list.append({"$or": [{"created_at": {"$gte": start_date, "$lt": end_date}}]})

# Add a filter for the selected crops
menu = st.sidebar.multiselect(
    "Select the kind of crops:",
    [
        "Aguacate",
        "Mango",
        "Almendro",
        "Olivo",
        "Algarrobo",
        "Encina",
        "Cereal",
        "Erial",
    ],
)

# Add a query for the selected crops to the query list
if menu != []:
    menu_query = []
    for cp in menu:
        menu_query.append({"Crop": {"$regex": cp, "$options": "i"}})
    if len(menu_query) > 1:
        query_list.append({"$or": menu_query})
    elif len(menu_query) == 1:
        query_list.append({"$or": menu_query})

# Add a filter for the selected variety of mango if mango is selected
if "Mango" in menu:
    mango_menu = st.sidebar.multiselect(
        "Select a variety of Mango",
        [
            "Osteen",
            "Keitt",
            "Kent",
            "Palmer",
            "Tommy Atkins",
            "Irwin",
            "Ataulfo",
            "Sensation",
        ],
    )

    if mango_menu != []:
        mango_query = []
        for var in mango_menu:
            mango_query.append({"Variety": {"$regex": var, "$options": "i"}})
        if len(mango_query) > 1:
            query_list.append({"$or": mango_query})
        elif len(mango_query) == 1:
            query_list.append(mango_query[0])
        variety_selection(mango_query, "Mango")

# Add a filter for the selected variety of mango if avocado is selected
if "Avocado" in menu:
    avocado_menu = st.sidebar.multiselect(
        "Select a variety of Avocado:",
        [
            "Hass",
            "Fuerte",
            "Bacon",
            "Zutano",
            "Pinkerton",
            "Lamb Hass",
            "Reed",
            "Maluma Hass",
        ],
    )
    if avocado_menu != []:
        avocado_query = []
        for var in avocado_menu:
            avocado_query.append({"Variety": {"$regex": var, "$options": "i"}})
        if len(avocado_query) > 1:
            query_list.append({"$or": avocado_query})
        elif len(avocado_query) == 1:
            query_list.append(avocado_query[0])
        # Call a function to update the map with the selected variety markers
        variety_selection(avocado_query, "Aguacate")

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
    num_pics = len(document["Pictures"])

    html_list = []
    for i in range(num_pics):
        # Retrieve and encode the image from Minio
        minio_image = (
            client.get_object(settings.MINIO_BUCKET, document["Pictures"][i])
        ).read()
        encoded = base64.b64encode(minio_image).decode()
        # Create HTML code to display the image
        html = f""" <table>
                            <tr>
                            <td><strong><img src= 'data:image/png;base64,{encoded}'></strong></td>
                            </tr>
                        </table>"""
        html_list.append(html)
    html = "".join(html_list)
    # Create a popup containing the images and add a marker to the map
    iframe = folium.IFrame(html, width="100%", ratio="50%")
    popup = folium.Popup(iframe, min_width=500, max_width=150)
    marker = folium.Marker(
        [document["Latitude"], document["Longitude"]],
        popup=(popup),
        tooltip=document["Crop"],
    ).add_to(crop_map)
    crop_map.add_child(marker)

# Add the map to the Streamlit app
folium_static(crop_map, height=500, width=1300)

import altair as alt
from minio_client import minio_connection
import folium
import pandas as pd
import streamlit as st
import datetime
from streamlit_folium import folium_static
from mongo_client import get_collection_object
from utils import generate_map, popup_html
from config import settings
import base64


# Set the page configuration
st.set_page_config(layout="wide")

collection = get_collection_object(
    settings.MONGO_DB_FLORA, settings.MONGO_COLLECTION_FLORA
)

client = minio_connection()


st.title("Flora map")

crop_map = generate_map([37.3522, -4.64363], 8)


with st.sidebar.form(key="my_form"):

    id_unique = collection.distinct("_id")
    _id = st.multiselect("ID", id_unique)

    start_date = st.date_input(
        "Start date", value=datetime.date(1980, 1, 1)
    )
    start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time())

    end_date = st.date_input("End date")
    end_date = datetime.datetime.combine(end_date, datetime.datetime.min.time())
    

    community_unique = collection.distinct("Community", {"Community": { "$ne": None }})
    community = st.multiselect("Community", community_unique)

    subcommunity_unique = collection.distinct("Subcommunity", {"Subcommunity": { "$ne": None }})
    subcommunity = st.multiselect("Subcommunity", subcommunity_unique)

    natural_site_uniques = collection.distinct("Natural_Site", {"Natural_Site": { "$ne": None }})
    natural_site = st.multiselect("Natural Site", natural_site_uniques)

    species_unique = collection.distinct("Species.Name", {"Species.Name": { "$ne": None }})
    species = st.multiselect("Species name", species_unique)

    author_unique = collection.distinct("Authors", {"Authors": { "$ne": None }})
    author = st.multiselect("Author", author_unique)

    location = st.text_input("Location")
    if location and not all(elem == "" for elem in location):
        location = location.split(",")
        cnt = 0
        for element in location:
            if element != "":
                for result in collection.find(
                    {"Location": {"$regex": element, "$options": "i"}}
                ):
                    cnt += 1
        if cnt == 0:
            st.sidebar.error("No one location found.")

    submit_button = st.form_submit_button(label="Filter", help="Submit Button")

query_list = []

if start_date and end_date:
    query_list.append({"created_at": {"$gte": start_date, "$lte": end_date}})

if start_date and not end_date:
    query_list.append({"created_at": {"$gte": start_date}})

if not start_date and end_date:
    query_list.append({"created_at": {"$lte": end_date}})

if community:
    community_exp = []
    for particular_community in community:
        if len(particular_community) > 0:
            community_empty = False
            community_exp.append(
                {"Community": {"$regex": particular_community, "$options": "i"}}
            )
    if len(community_exp) > 1:
        community_dict = {"$or": community_exp}
        query_list.append(community_dict)
    elif len(community_exp) == 1:
        query_list.append(community_exp[0])


if subcommunity:
    subcommunity_exp = []
    for particular_subcommunity in subcommunity:
        if len(particular_subcommunity) > 0:
            subcommunity_empty = False
            subcommunity_exp.append(
                {"Subcommunity": {"$regex": particular_subcommunity, "$options": "i"}}
            )
    if len(subcommunity_exp) > 1:
        subcommunity_dict = {"$or": subcommunity_exp}
        query_list.append(subcommunity_dict)
    elif len(subcommunity_exp) == 1:
        query_list.append(subcommunity_exp[0])


if author:
    author_exp = []
    for particular_author in author:
        if len(particular_author) > 0:
            author_empty = False
            author_exp.append(
                {"Authors": {"$regex": particular_author, "$options": "i"}}
            )
    if len(author_exp) > 1:
        author_dict = {"$or": author_exp}
        query_list.append(author_dict)
    elif len(author_exp) == 1:
        query_list.append(author_exp[0])

if _id:
    id_exp = []
    for particular_id in _id:
        if len(particular_id) > 0:
            id_empty = False
            id_exp.append({"_id": {"$regex": particular_id, "$options": "i"}})
    if len(id_exp) > 1:
        id_dict = {"$or": id_exp}
        query_list.append(id_dict)
    elif len(id_exp) == 1:
        query_list.append(id_exp[0])


if species:

    species_exp = []
    for particular_species in species:
        if len(particular_species) > 0:
            species_empty = False
            species_exp.append(
                {"Species.Name": {"$regex": particular_species, "$options": "i"}}
            )
    if len(species_exp) > 1:
        species_dict = {"$and": species_exp}
        query_list.append(species_dict)
    elif len(species_exp) == 1:
        query_list.append(species_exp[0])


if location:
    location_exp = []
    for particular_location in location:
        if len(particular_location) > 0:
            location_empty = False
            location_exp.append(
                {"Location": {"$regex": particular_location, "$options": "i"}}
            )
    if len(location_exp) > 1:
        location_dict = {"$or": location_exp}
        query_list.append(location_dict)
    elif len(location_exp) == 1:
        query_list.append(location_exp[0])

if natural_site:
    natural_site_exp = []
    for particular_natural_site in natural_site:
        if len(particular_natural_site) > 0:
            natural_site_empty = False
            natural_site_exp.append(
                {"Natural_Site": {"$regex": particular_natural_site, "$options": "i"}}
            )
    if len(natural_site_exp) > 1:
        natural_site_dict = {"$or": natural_site_exp}
        query_list.append(natural_site_dict)
    elif len(natural_site_exp) == 1:
        query_list.append(natural_site_exp[0])


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


if submit_button:
    for document in cursor:

        num_pics = len(document["Pictures"])

        # print("sdffdddd", )
        # There are some sample without location
        if document["Latitude"] and document["Longitude"]:
            # print("cccccc",document)
            marker = folium.Marker(
                [document["Latitude"], document["Longitude"]],
                popup=document["Community"],
                tooltip=document["Community"],
            ).add_to(crop_map)
            crop_map.add_child(marker)


folium_static(crop_map, height=700, width=1300)

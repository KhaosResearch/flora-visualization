
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

collection = get_collection_object(settings.MONGO_DB_FLORA, settings.MONGO_COLLECTION_FLORA)

client = minio_connection()


st.title("Flora map")

crop_map = generate_map([37.1822, -3.93363], 7)


# Initialize the query list with a query for the selected dates
query_list = []
st.sidebar.title("Filtrar flora")

ss = collection.distinct("Authors")
print("fffffffffffffffffffffffffffffffffffffffffffffff",ss)

dff= collection.distinct("Pictures")
print("trhbfxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxff",dff)
community= st.sidebar.text_input("Community")

if community != "":
    community= community.split(',')
    cnt = 0
    print("jjjjjjjjjjjjjjjjjjjjjjjjjjj",community)
    for element in community:
        if collection.find(
            {"Community": {"$regex": element, "$options": "i"}}
            ):
            cnt += 1
            
    if cnt == 0:
        st.sidebar.error("No one community found.")
# fecha --> preguntar porque en la BD está siempre a null
currentDateTime = datetime.datetime.now()
date = currentDateTime.date()
year = date.strftime("%Y")

community_start_year = st.sidebar.text_input('Community start year')
community_end_year = st.sidebar.text_input('Community end year')


subcommunity_start_year = st.sidebar.text_input('Subcommunity start year')
subcommunity_end_year = st.sidebar.text_input('Subcommunity end year')


project = st.sidebar.text_input('Project')
if project:
        if collection.find({"Project": {"$regex": project, "$options": "i"}}) == None:
            st.sidebar.error("Project" + project + " is not present in inventories.")

natural_site_uniques = collection.distinct("Natural_Site")
natural_site = st.sidebar.selectbox('Natural Site',["Select a natural site"]+ natural_site_uniques)
print("fffff",natural_site)
if natural_site != "Select a natural site":
        if collection.find({"Natural_Site": {"$regex": natural_site, "$options": "i"}}) == None:
            st.sidebar.error("Natural_Site" + natural_site + " is not present in inventories.")


altitude = st.sidebar.text_input('Altitude')
if altitude:
        if collection.find({"Altitude": {"$eq": int(altitude)}}) == None:
            st.sidebar.error("Altitude" + altitude + " is not present in inventories.")

lithology = st.sidebar.text_input('Lithology')
if lithology:
        if collection.find({"Lithology": {"$regex": lithology, "$options": "i"}}) == None:
            st.sidebar.error("Lithology" + lithology + " is not present in inventories.")

plot_orientation = st.sidebar.text_input('Plot Orientation')
if plot_orientation:
        if collection.find({"Plot_Orientation": {"$regex": plot_orientation, "$options": "i"}}) == None:
            st.sidebar.error("Plot_Orientation" + plot_orientation + " is not present in inventories.")

plot_slope = st.sidebar.text_input('Plot slope')
if plot_slope:
        if collection.find({"Plot_Slope": {"$eq": plot_slope }}) == None:
            st.sidebar.error("Plot_Slope" + plot_slope + " is not present in inventories.")


specie = st.sidebar.text_input('Specie name')
if specie:
        if collection.find({"Species.Name": {"$regex": specie, "$options": "i"}}) == None:
            st.sidebar.error("Species.Name" + specie + " is not present in inventories.")

location = st.sidebar.text_input('Location')
if location and not all(elem == "" for elem in location):
        location= location.split(',')
        cnt = 0
        for element in location:
            if element != "":
                for result in collection.find(
                    {"Location": {"$regex": element, "$options": "i"}}
                ):
                    cnt += 1
        if cnt == 0:
            st.sidebar.error("No one location found.")



final_list = []
delimiter = ";"
query_list = []
author_empty = True
location_empty = True
species_empty = True
community_empty = True


if community != "":
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

if community_start_year != "" and community_end_year != "":
        query_list.append(
            {
                "Community_Year": {
                    "$gte": int(community_start_year),
                    "$lte": int(community_end_year),
                }
            }
        )
if community_start_year != "" and community_end_year == "":
        query_list.append({"Community_Year": {"$gt": int(community_start_year)}})

if community_start_year == "" and community_end_year != "":
        query_list.append({"Community_Year": {"$lt": int(community_end_year)}})
if subcommunity_start_year != "" and subcommunity_end_year != "":
        query_list.append(
            {
                "Community_Year": {
                    "$gte": int(subcommunity_start_year),
                    "$lte": int(subcommunity_end_year),
                }
            }
        )
if subcommunity_start_year != "" and subcommunity_end_year == "":
        query_list.append({"Community_Year": {"$gt": int(subcommunity_start_year)}})

if subcommunity_start_year == "" and subcommunity_end_year != "":
        query_list.append({"Community_Year": {"$lt": int(subcommunity_end_year)}})
if project:
        query_list.append({"Project": {"$regex": project, "$options": "i"}})

if community_start_year != "" and community_end_year != "":
        query_list.append(
            {
                "Community_Year": {
                    "$gte": int(community_start_year),
                    "$lte": int(community_end_year),
                }
            }
        )
if specie:
        query_list.append({"Species.Name": {"$regex": specie, "$options": "i"}})

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

if natural_site != "Select a natural site":
        query_list.append({"Natural_Site": {"$regex": natural_site, "$options": "i"}})


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

aa = collection.distinct("Natural_Site")
print("gggggggggggg",aa)

#print("fg",cursor)
# For each matching document, create a marker on the map with a popup containing the document's images
# for document in cursor:
    
#     num_pics = len(document["Pictures"])
    
    
#     #print("sdffdddd", )
#     #There are some sample without location
#     if document["Latitude"] and document["Longitude"]:
#         #print("cccccc",document)
#         marker = folium.Marker(
#                 [document["Latitude"], document["Longitude"]],
#                 popup=document["Community"],
#                 tooltip=document["Community"],
#             ).add_to(crop_map) 
#         crop_map.add_child(marker)
        
    

folium_static(crop_map, height=500, width=1300)



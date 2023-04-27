import base64
import datetime
import io
import os

import folium
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

from config import settings
from minio_client import minio_connection
from mongo_client import get_collection_object
from utils import (diacritic_sensitive_regex, generate_map,
                   popup_html_from_mongo)

# Set the page configuration
st.set_page_config(layout="wide")

collection = get_collection_object(
    settings.MONGO_DB_FLORA, settings.MONGO_COLLECTION_FLORA
)

client = minio_connection(
    settings.MINIO_ACCESS_KEY_FLORA, settings.MINIO_SECRET_KEY_FLORA
)

st.title("Flora map")
date_warning = False
soil_map = generate_map([37.3522, -4.64363], 8)

query_list = []
option = st.sidebar.selectbox(
    "Select the form in which you want to visualize data", ("Filter data", "View all")
)


if option == "Filter data":
    with st.sidebar.form(key="my_form"):

        id_unique = collection.distinct("_id")
        _id = st.multiselect("ID", id_unique, help="Optional")

        dates_unique = collection.distinct("created_at")
        dates_unique.sort()
        min_date = dates_unique[0]
        max_date = datetime.date.today()

        range_date = st.date_input("Date range", (min_date, max_date))
        start_date = False
        end_date = False
        try:
            start_date = datetime.datetime.combine(
                range_date[0], datetime.datetime.min.time()
            )
            end_date = datetime.datetime.combine(
                range_date[1], datetime.datetime.min.time()
            )
        except:
            date_warning = True
            st.warning("Incomplete range")

        community_unique = collection.distinct(
            "Community", {"Community": {"$ne": None}}
        )

        community = st.multiselect("Community", community_unique, help="Optional")

        subcommunity_unique = collection.distinct(
            "Subcommunity", {"Subcommunity": {"$ne": None}}
        )
        subcommunity = st.multiselect(
            "Subcommunity", subcommunity_unique, help="Optional"
        )

        natural_site_uniques = collection.distinct(
            "Natural_Site", {"Natural_Site": {"$ne": None}}
        )
        natural_site = st.multiselect(
            "Natural Site", natural_site_uniques, help="Optional"
        )

        species_unique = collection.distinct(
            "Species.Name", {"Species.Name": {"$ne": None}}
        )
        species = st.multiselect("Species name", species_unique, help="Optional")

        author_unique = collection.distinct("Authors", {"Authors": {"$ne": None}})
        author = st.multiselect("Author", author_unique, help="Optional")

        location = st.text_input(
            "Location",
            help=f"Optional. Search for multiple locations by typing them with a comma between them. "
            f"Due to the disparity in the data, the input for this input will be a string of locations separated by commas,"
            f"so if you want to search for Cabo de gata and Sierra de las nieves, for example, the way to enter that data would be"
            f"'Cabo de gata,Sierra de las nieves' (not including single quotes('')). The accents and capitalization are checked,"
            f"so the word 'Rio' and 'riO' will get the same results.",
        )
        # Check if this location is in the DB
        if location and not all(elem == "" for elem in location):
            location = location.split(",")
            cnt = 0
            for element in location:
                if element != "":
                    for result in collection.find(
                        {
                            "Location": {
                                "$regex": diacritic_sensitive_regex(element),
                                "$options": "i",
                            }
                        }
                    ):
                        cnt += 1
            if cnt == 0:
                st.sidebar.error("No one location found.")

        submit_button = st.form_submit_button(label="Search", help="Submit Button")

    if start_date and end_date:
        query_list.append({"created_at": {"$gte": start_date, "$lte": end_date}})

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
                    {
                        "Subcommunity": {
                            "$regex": particular_subcommunity,
                            "$options": "i",
                        }
                    }
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
                    {
                        "Location": {
                            "$regex": diacritic_sensitive_regex(particular_location),
                            "$options": "i",
                        }
                    }
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
                    {
                        "Natural_Site": {
                            "$regex": particular_natural_site,
                            "$options": "i",
                        }
                    }
                )
        if len(natural_site_exp) > 1:
            natural_site_dict = {"$or": natural_site_exp}
            query_list.append(natural_site_dict)
        elif len(natural_site_exp) == 1:
            query_list.append(natural_site_exp[0])

if option == "View all":
    with st.sidebar.form(key="my_form"):
        submit_button = st.form_submit_button(label="Search", help="Submit Button")

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
long_lat = []

if submit_button and not date_warning:  # or all_samples
    for document in cursor:
        num_pics = len(document["Pictures"])
        html_list = []
        long_lat.append([document["Latitude"], document["Longitude"]])
        for i in range(num_pics):
            MAX_SIZE = 1000000
            # delete the bucket from the path in mongo. If not, in client.getobject the bucket name is duplicated
            path = (document["Pictures"][i]).split("/", 1)[1]
            # Retrieve and encode the image from Minio
            minio_image = (client.get_object(settings.MINIO_BUCKET_FLORA, path)).read()

            # Load the image into PIL
            image = Image.open(io.BytesIO(minio_image))
            if len(minio_image) > MAX_SIZE:
                # Calculate the new size while maintaining aspect ratio
                w, h = image.size
                ratio = w / h
                new_w = int((MAX_SIZE / 2) ** 0.5 * ratio)
                new_h = int((MAX_SIZE / 2) ** 0.5 / ratio)

                # Resize the image and save to a buffer
                image = image.resize((new_w, new_h))
                buffer = io.BytesIO()

                # Get the file extension of the original image
                file_extension = os.path.splitext(path)[1].lower()

                # Save the resized image to a buffer in the appropriate format
                if file_extension == ".png":
                    image.save(buffer, format="PNG", optimize=True, quality=75)
                else:
                    image.save(buffer, format="JPEG", optimize=True, quality=75)

                # Get the bytes of the resized image
                resized_image = buffer.getvalue()
            else:
                # Use the original image if it's already small enough
                resized_image = minio_image

            encoded = base64.b64encode(resized_image).decode()
            # Create HTML code to display the image
            html = f""" <table>
                                <tr>
                                <td><strong><img src= 'data:image/png;base64,{encoded}'></strong></td>
                                </tr>
                            </table>"""
            html_list.append(html)

        html_img = "".join(html_list)
        html = popup_html_from_mongo(document, html_img)
        iframe = folium.IFrame(html, width=800, height=520)
        popup = folium.Popup(iframe)

        # There are some sample without longitude-latitude
        if document["Latitude"] and document["Longitude"]:
            marker = folium.Marker(
                [document["Latitude"], document["Longitude"]],
                popup=popup,
                tooltip=document["Community"],
            ).add_to(soil_map)
            soil_map.add_child(marker)

soil_map.fit_bounds(long_lat)

folium_static(soil_map, height=700, width=1300)

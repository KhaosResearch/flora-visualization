import datetime
import statistics as stats

import folium
import streamlit as st
from config import settings
from folium.plugins import HeatMap, MarkerCluster
from minio_client import minio_connection
from mongo_client import get_collection_object
from streamlit_folium import folium_static
from utils import popup_html_from_mongo

# Set the page configuration
st.set_page_config(layout="wide")

collection = get_collection_object(
    settings.MONGO_DB_FLORA, settings.MONGO_COLLECTION_FLORA
)

client = minio_connection(
    settings.MINIO_ACCESS_KEY_FLORA, settings.MINIO_SECRET_KEY_FLORA
)
query_list = []


st.sidebar.title("Filter data")
with st.sidebar.form(key="my_form"):
    dates_unique = collection.distinct("eventDate")
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

    province_unique = collection.distinct(
        "stateProvince", {"stateProvince": {"$ne": None}}
    )

    province = st.multiselect("Province", province_unique, help="Optional")

    institution_unique = collection.distinct(
        "institutionCode", {"institutionCode": {"$ne": None}}
    )
    institution = st.multiselect(
        "Institution code", institution_unique, help="Optional"
    )

    natural_site_uniques = collection.distinct(
        "NaturalSite", {"NaturalSite": {"$ne": None}}
    )
    natural_site = st.multiselect("Natural Site", natural_site_uniques, help="Optional")

    species_unique = collection.distinct("specieName", {"specieName": {"$ne": None}})
    species = st.multiselect("Species name", species_unique, help="Optional")

    recorded_by_unique = collection.distinct(
        "recordedBy", {"recordedBy": {"$ne": None}}
    )
    recorded_by = st.multiselect("Recorded by", recorded_by_unique, help="Optional")

    submit_button = st.form_submit_button(label="Search", help="Submit Button")

if start_date and end_date:
    query_list.append({"eventDate": {"$gte": start_date, "$lte": end_date}})
if province:
    province_exp = []
    for particular_province in province:
        if len(particular_province) > 0:
            province_empty = False
            province_exp.append(
                {"stateProvince": {"$regex": particular_province, "$options": "i"}}
            )
    if len(province_exp) > 1:
        query_list.append({"$or": province_exp})

    elif len(province_exp) == 1:
        query_list.append({"$or": province_exp})

if institution:
    institution_exp = []
    for particular_institution in institution:
        if len(particular_institution) > 0:
            institution_empty = False
            institution_exp.append(
                {"institutionCode": {"$regex": particular_institution, "$options": "i"}}
            )
    if len(institution_exp) > 1:
        query_list.append({"$or": institution_exp})
    elif len(institution_exp) == 1:
        query_list.append({"$or": institution_exp})

if recorded_by:
    recorded_by_exp = []
    for particular_recorded_by in recorded_by:
        if len(particular_recorded_by) > 0:
            recorded_by_empty = False
            recorded_by_exp.append(
                {"recorded_bys": {"$regex": particular_recorded_by, "$options": "i"}}
            )
    if len(recorded_by_exp) > 1:
        query_list.append({"$or": recorded_by_exp})
    elif len(recorded_by_exp) == 1:
        query_list.append({"$or": recorded_by_exp})


if species:
    species_exp = []
    for particular_species in species:
        if len(particular_species) > 0:
            species_empty = False
            species_exp.append(
                {"specieName": {"$regex": particular_species, "$options": "i"}}
            )
    if len(species_exp) > 1:
        query_list.append({"$or": species_exp})
    elif len(species_exp) == 1:
        query_list.append({"$or": species_exp})

if natural_site:
    natural_site_exp = []
    for particular_natural_site in natural_site:
        if len(particular_natural_site) > 0:
            natural_site_empty = False
            natural_site_exp.append(
                {"NaturalSite": {"$regex": particular_natural_site, "$options": "i"}}
            )
    if len(natural_site_exp) > 1:
        query_list.append({"$or": natural_site_exp})
    elif len(natural_site_exp) == 1:
        query_list.append({"$or": natural_site_exp})


try:
    print("Query list", query_list)
    # If the query list is not empty, use it to find matching documents in the MongoDB collection
    if len(query_list) > 0:
        cursor_list = list(collection.find({"$and": query_list}))

    # If the query list is empty, find all documents in the collection
    else:
        cursor_list = list(collection.find())
except Exception as e:
    print(e)

latitude_location = []
longitude_location = []
if len(query_list) > 1:
    for document in cursor_list:
        if document["decimalLatitude"]:
            latitude_location.append(
                float(document["decimalLatitude"].replace(",", "."))
            )
            longitude_location.append(
                float(document["decimalLongitude"].replace(",", "."))
            )

    if latitude_location:
        median_latitude = stats.median(latitude_location)
        median_longitude = stats.median(longitude_location)
    else:
        median_latitude = 37.5396745
        median_longitude = -4.5424751
else:
    median_latitude = 37.5396745
    median_longitude = -4.5424751

st.title("Floras")

# Create a folium map centered on the median of latitude and longitude
flora_map = folium.Map(
    location=[median_latitude, median_longitude],
    zoom_start=8,  # Set the maximum zoom level
    width="100%",
    height="100%",
    tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    attr="Google Satellite",
)

# Create a marker cluster layer
marker_cluster = MarkerCluster(name="Marcadores", show=True).add_to(flora_map)

# For each matching document, create a marker on the map with a popup containing the document's images
long_lat = []
heatmap_long_lat = []

# For each matching document, create a marker on the map with a popup containing the document's images


if submit_button:  # or all_samples
    for document in cursor_list:
        pictures_list_link = []
        if "Pictures" in document:
            num_pics = len(document["Pictures"])
            for i in range(num_pics):
                # Get the image from Minio
                minio_image = client.presigned_get_object(
                    settings.MINIO_BUCKET_FLORA,
                    document["Pictures"][i].replace("enbic2lab/", ""),
                )
                pictures_list_link.append(minio_image)
        long_lat.append([float(document["decimalLatitude"].replace(",", ".")), float(document["decimalLongitude"].replace(",", "."))])
        # There are some sample without longitude-latitude      
        if float(document["decimalLatitude"].replace(",", ".")) and float(document["decimalLongitude"].replace(",", ".")):
            heatmap_long_lat.append([float(document["decimalLatitude"].replace(",", ".")), float(document["decimalLongitude"].replace(",", "."))])
            document["Pictures"] = pictures_list_link
            # Create the HTML code to display the table
            html = popup_html_from_mongo(document)
            iframe = folium.IFrame(html, width=650, height=650)
            popup = folium.Popup(iframe, lazy=True)
            marker = folium.Marker(
                [float(document["decimalLatitude"].replace(",", ".")), float(document["decimalLongitude"].replace(",", "."))],
                popup=popup,
                tooltip=document["specieName"],
            )
            marker_cluster.add_child(marker)


# Create a HeatMap layer with the heatmap data
heatmap_layer = HeatMap(heatmap_long_lat, name="HeatMap", show=True)

# Add the heatmap layer and marker layer to the map
heatmap_layer.add_to(flora_map)
marker_cluster.add_to(flora_map)

# Add the layer control to the map
folium.LayerControl().add_to(flora_map)

# Add the map to the Streamlit app
folium_static(flora_map, width=1200, height=800)
import streamlit as st
from pymongo import MongoClient
from pymongo.collection import Collection

from config import settings


@st.cache_resource
def mongo_connection() -> MongoClient:
    print("Creating mongo client")
    client = MongoClient(
        host={settings.MONGO_URI}
    )
    return client


def get_collection_object(db, collection) -> Collection:
    client = mongo_connection()

    return client[db][collection]

from minio import Minio
import streamlit as st
from config import settings


@st.cache_resource
def minio_connection(access_key, secret_key) -> Minio:
    print("Creating minio client")
    client = Minio(
        settings.MINIO_HOST,
        access_key=access_key,
        secret_key=secret_key,
        secure = True
        
    )
    return client

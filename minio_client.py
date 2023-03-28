from minio import Minio
import streamlit as st
from config import settings


@st.cache_resource
def minio_connection() -> Minio:
    print("Creating minio client")
    client = Minio(
        settings.MINIO_HOST,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure = True
        
    )
    return client

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Try Streamlit Cloud secrets first, then fall back to .env
try:
    API_KEY = st.secrets["API_KEY"]
except Exception:
    API_KEY = os.getenv("API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
MODEL_NAME = "gemini-2.0-flash"

# Supported file types for job details extraction
JOB_FILE_TYPES = ['pdf', 'docx', 'doc', 'txt', 'png', 'jpg', 'jpeg', 'webp', 'html', 'json', 'csv', 'xlsx', 'pptx', 'eml', 'msg']
IMAGE_TYPES = {'png', 'jpg', 'jpeg', 'webp'}

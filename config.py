import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"

# Supported file types for job details extraction
JOB_FILE_TYPES = ['pdf', 'docx', 'doc', 'txt', 'png', 'jpg', 'jpeg', 'webp', 'html', 'json', 'csv', 'xlsx', 'pptx', 'eml', 'msg']
IMAGE_TYPES = {'png', 'jpg', 'jpeg', 'webp'}

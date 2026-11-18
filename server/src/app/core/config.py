import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

JINA_API_KEY = os.environ["JINA_API_KEY"]
NVIDIA_API_KEY = os.environ["NVIDIA_API_KEY"]
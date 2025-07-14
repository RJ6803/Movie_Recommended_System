# src/omdb_utils.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

def get_movie_details(title):
    url = f"http://www.omdbapi.com/?t={title}&plot=full&apikey={OMDB_API_KEY}"
    try:
        res = requests.get(url, timeout=5).json()
        if res.get("Response") == "True":
            return res.get("Plot", "N/A"), res.get("Poster", "N/A")
    except requests.RequestException:
        pass
    return "N/A", "N/A"

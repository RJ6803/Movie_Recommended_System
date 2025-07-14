# src/recommend.py

import joblib
import logging
import pandas as pd
import gdown
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("recommend.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# Ensure models directory exists
os.makedirs("models", exist_ok=True)

# Check and download cosine_sim.pkl from Google Drive if missing
file_path = "models/cosine_sim.pkl"
if not os.path.exists(file_path):
    logging.info("📥 Downloading cosine_sim.pkl from Google Drive...")
    try:
        # Replace this ID with your actual file ID
        file_id = "1a-AOLnwBD4zZn2ikBWKoVDPoEaOBRsYS"
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, file_path, quiet=False)
        logging.info("✅ cosine_sim.pkl downloaded successfully.")
    except Exception as e:
        logging.error("❌ Failed to download cosine_sim.pkl: %s", e)

class MovieRecommender:
    def __init__(self, df_path='models/df_cleaned.pkl',
                 sim_path='models/cosine_sim.pkl'):
        try:
            self.df = joblib.load(df_path)
            self.similarity = joblib.load(sim_path)
            logging.info("✅ Data loaded successfully from pickle files.")
        except Exception as e:
            logging.error("❌ Failed to load model files: %s", e)
            self.df = None
            self.similarity = None

    def get_recommendations(self, movie_title, top_n=5):
        if self.df is None or self.similarity is None:
            logging.error("❌ Model data not loaded.")
            return None

        movie_title = movie_title.lower()
        idx_list = self.df[self.df['title'].str.lower() == movie_title].index

        if len(idx_list) == 0:
            logging.warning("⚠️ Movie not found in dataset: %s", movie_title)
            return None

        idx = idx_list[0]
        sim_scores = list(enumerate(self.similarity[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
        movie_indices = [i[0] for i in sim_scores]

        return self.df.iloc[movie_indices][['title', 'overview', 'genres']].reset_index(drop=True)

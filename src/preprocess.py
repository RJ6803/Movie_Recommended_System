import pandas as pd
import re
import nltk
import os
import joblib
import logging
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

logging.info("🚀 Starting preprocessing...")

stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    text = re.sub(r"[^a-zA-Z\s]", "", str(text))
    text = text.lower()
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

try:
    df = pd.read_csv("data/movie.csv")
    logging.info("✅ Dataset loaded. Rows: %d", len(df))
except Exception as e:
    logging.error("❌ Failed to load CSV: %s", e)
    raise e

required_columns = ["genres", "keywords", "overview", "title"]
df = df[required_columns].dropna().reset_index(drop=True)
df['combined'] = df['genres'] + ' ' + df['keywords'] + ' ' + df['overview']
df['cleaned_text'] = df['combined'].apply(preprocess_text)

logging.info("🔠 Vectorizing text...")
tfidf = TfidfVectorizer(max_features=5000)
tfidf_matrix = tfidf.fit_transform(df['cleaned_text'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

os.makedirs("models", exist_ok=True)
joblib.dump(df, 'models/df_cleaned.pkl')
joblib.dump(tfidf_matrix, 'models/tfidf_matrix.pkl')
joblib.dump(cosine_sim, 'models/cosine_sim.pkl')

logging.info("✅ Preprocessing complete.")

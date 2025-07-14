import os
from flask import Flask, request, render_template_string
from dotenv import load_dotenv
from recommend import MovieRecommender
import requests

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

app = Flask(__name__)
recommender = MovieRecommender()

def get_movie_details(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}&plot=short"
    try:
        res = requests.get(url, timeout=5).json()
        if res.get("Response") == "True":
            return res.get("Plot", "N/A"), res.get("Poster", "N/A")
    except Exception as e:
        print(f"OMDb fetch error for {title}: {e}")
    return "N/A", "N/A"

@app.route("/", methods=["GET", "POST"])
def home():
    movie_title = ""
    recommendations = []
    error = None

    if request.method == "POST":
        movie_title = request.form.get("movie")
        if movie_title:
            recs = recommender.get_recommendations(movie_title)
            if recs is None or recs.empty:
                error = f"No recommendations found for '{movie_title}'."
            else:
                for _, rec in recs.iterrows():
                    plot, poster = get_movie_details(rec['title'])
                    recommendations.append({
                        "title": rec["title"],
                        "genres": rec["genres"],
                        "overview": plot,     # Use plot from OMDb
                        "poster": poster
                    })

    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Movie Recommendation System</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        </head>
        <body>
        <div class="container mt-5">
            <h1 class="mb-4">🎬 Movie Recommendation System</h1>
            <form method="post">
                <div class="mb-3">
                    <input type="text" class="form-control" name="movie" placeholder="Enter a movie title" value="{{ movie_title }}">
                </div>
                <button type="submit" class="btn btn-primary">Recommend</button>
            </form>
            {% if error %}
                <div class="alert alert-danger mt-3">{{ error }}</div>
            {% endif %}
            {% if recommendations %}
                <h3 class="mt-4">Top Recommendations:</h3>
                <div class="row mt-3">
                    {% for movie in recommendations %}
                        <div class="col-md-4">
                            <div class="card mb-4">
                                {% if movie.poster and movie.poster != "N/A" %}
                                    <img src="{{ movie.poster }}" class="card-img-top" alt="Poster for {{ movie.title }}">
                                {% else %}
                                    <div class="text-center p-3">Poster not available</div>
                                {% endif %}
                                <div class="card-body">
                                    <h5 class="card-title">{{ movie.title }}</h5>
                                    <p><strong>Genres:</strong> {{ movie.genres }}</p>
                                    <p class="card-text">{{ movie.overview }}</p>
                                </div>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        </div>
        </body>
        </html>
    ''', movie_title=movie_title, recommendations=recommendations, error=error)

if __name__ == "__main__":
    app.run(debug=True)

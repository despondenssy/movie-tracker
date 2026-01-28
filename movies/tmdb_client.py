"""
Low-level client for TMDB API.
Contains functions for searching movies/series and fetching movie/series details.

Uses the requests library for HTTP requests.
"""

import os
import requests

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

def tmdb_search_movie(query):
    """Search movies/series by title"""
    url = f"{TMDB_BASE_URL}/search/multi"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "include_adult": False,
    }

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
    except requests.RequestException as e:
        return []

    data = resp.json()
    return data.get("results", [])

def tmdb_get_movie_details(tmdb_id, media_type="movie"):
    """Get movie/series details by TMDB ID"""
    url = f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}"
    params = {"api_key": TMDB_API_KEY}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

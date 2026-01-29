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


def tmdb_get_trending(media_type="all", time_window="week"):
    """Get trending movies/TV shows (media_type: all/movie/tv, time_window: day/week)"""
    url = f"{TMDB_BASE_URL}/trending/{media_type}/{time_window}"
    params = {"api_key": TMDB_API_KEY}
    
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
    except requests.RequestException:
        return []
    
    data = resp.json()
    return data.get("results", [])


def tmdb_get_popular(media_type="movie"):
    """Get popular movies or TV shows (media_type: movie/tv)"""
    url = f"{TMDB_BASE_URL}/{media_type}/popular"
    params = {"api_key": TMDB_API_KEY}
    
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
    except requests.RequestException:
        return []
    
    data = resp.json()
    return data.get("results", [])


def tmdb_get_top_rated(media_type="movie"):
    """Get top rated movies or TV shows (media_type: movie/tv)"""
    url = f"{TMDB_BASE_URL}/{media_type}/top_rated"
    params = {"api_key": TMDB_API_KEY}
    
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
    except requests.RequestException:
        return []
    
    data = resp.json()
    return data.get("results", [])


def tmdb_get_similar(tmdb_id, media_type="movie"):
    """Get similar movies or TV shows (media_type: movie/tv)"""
    url = f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}/similar"
    params = {"api_key": TMDB_API_KEY}
    
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
    except requests.RequestException:
        return []
    
    data = resp.json()
    return data.get("results", [])

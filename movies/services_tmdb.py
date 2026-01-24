"""
Service layer for importing data from TMDB into our Django Film and Genre models.

- Maps external JSON data to Django models.
- Checks for duplicates.
- Creates necessary genres.
"""

from .models import Film, Genre

def import_tmdb_movie(tmdb_data):
    """
    Import a movie or series from TMDB into our database.

    Ensures no duplicates by TMDB ID. Handles missing fields gracefully.
    Creates related genres if they don't exist.
    """

    tmdb_id = tmdb_data.get("id")
    if not tmdb_id:
        raise ValueError("TMDB data must contain an 'id' field")

    title = tmdb_data.get("title") or tmdb_data.get("name", "Unknown Title")

    if "release_date" in tmdb_data and tmdb_data["release_date"]:
        start_year = int(tmdb_data["release_date"][:4])
    elif "first_air_date" in tmdb_data and tmdb_data["first_air_date"]:
        start_year = int(tmdb_data["first_air_date"][:4])
    else:
        start_year = None

    type_ = "movie" if "title" in tmdb_data else "series"

    description = tmdb_data.get("overview", "")

    film, created = Film.objects.get_or_create(
        tmdb_id=tmdb_id,
        defaults={
            "title": title,
            "start_year": start_year,
            "type": type_,
            "description": description,
        }
    )

    tmdb_genres = tmdb_data.get("genres", [])
    for g in tmdb_genres:
        genre_obj, _ = Genre.objects.get_or_create(name=g["name"])
        film.genres.add(genre_obj)

    film.save()

    return film
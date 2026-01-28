from django.urls import path
from .views import (
    search_movies,
    add_movie,
    quick_add_movie,
    film_detail,
    set_film_status,
    upsert_review,
)

urlpatterns = [
    path("search/", search_movies, name="search_movies"),
    path("add-movie/", add_movie, name="add_movie"),
    path("quick-add/", quick_add_movie, name="quick_add_movie"),
    path("films/<int:film_id>/", film_detail, name="film_detail"),
    path("films/<int:film_id>/status/", set_film_status, name="set_film_status"),
    path("films/<int:film_id>/review/", upsert_review, name="upsert_review"),
]
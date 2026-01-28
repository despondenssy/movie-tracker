from django.urls import path
from .views import search_movies, add_movie, quick_add_movie, film_detail

urlpatterns = [
    path("search/", search_movies, name="search_movies"),
    path("add-movie/", add_movie, name="add_movie"),
    path("quick-add/", quick_add_movie, name="quick_add_movie"),
    path("films/<int:film_id>/", film_detail, name="film_detail"),
]
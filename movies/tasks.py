from celery import shared_task
from django.core.cache import cache
from .tmdb_client import tmdb_get_trending, tmdb_get_popular


@shared_task
def update_trending_cache():
    """Обновление кэша trending фильмов (раз в час)"""
    trending = tmdb_get_trending(media_type="all", time_window="week")[:12]
    cache.set('trending_week', trending, 60 * 60)  # 1 hour
    return f"Updated trending cache: {len(trending)} items"


@shared_task
def update_popular_cache():
    """Обновление кэша popular фильмов (раз в 6 часов)"""
    popular = tmdb_get_popular(media_type="movie")[:12]
    cache.set('popular_movies', popular, 60 * 60 * 6)  # 6 hours
    return f"Updated popular cache: {len(popular)} items"

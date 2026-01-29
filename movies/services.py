from django.db.models import Avg, Count
from .models import WatchStatus, Review, Film
from .tmdb_client import tmdb_get_similar


def set_watch_status(*, user, film, status):
    """
    Creates or updates watch status for a user and a film.

    Returns:
        watch_status (WatchStatus): object that was created or updated
        created (bool): True if created, False if updated
    """
    watch_status, created = WatchStatus.objects.update_or_create(
        user=user,
        film=film,
        defaults={"status": status},
    )

    return watch_status, created


def get_user_watchlist(*, user):
    """
    Returns all films with their watch statuses for a user.
    """
    return WatchStatus.objects.filter(
        user=user
    ).select_related("film")


def get_user_watched_count(*, user):
    return get_user_watched(user=user).count()


def get_user_watchlist_by_status(*, user, status):
    """
    Returns user's films filtered by watch status.
    """
    return get_user_watchlist(user=user).filter(status=status)


def get_user_watched(*, user):
    return get_user_watchlist_by_status(
        user=user,
        status=WatchStatus.Status.WATCHED
    )


def get_user_planned(*, user):
    return get_user_watchlist_by_status(
        user=user,
        status=WatchStatus.Status.PLANNED
    )


def get_user_watching(*, user):
    return get_user_watchlist_by_status(
        user=user,
        status=WatchStatus.Status.WATCHING
    )


def get_user_dropped(*, user):
    return get_user_watchlist_by_status(
        user=user,
        status=WatchStatus.Status.DROPPED
    )


def get_film_rating_stats(*, film):
    """
    Returns average rating and rating count for a film.

    If the film has no reviews, returns (None, 0).
    """
    stats = Review.objects.filter(
        film=film
    ).aggregate(
        avg_rating=Avg("rating"),
        rating_count=Count("id"),
    )

    return stats["avg_rating"], stats["rating_count"]


def get_user_recommendations(*, user, limit=20):
    """
    Generate personalized recommendations based on user's highly-rated films.
    
    Algorithm:
    1. Find films user rated 8-10
    2. Get similar films from TMDB for each
    3. Filter out already watched/in watchlist
    4. Remove duplicates, sort by TMDB rating
    
    Returns: List of dicts with TMDB movie data
    """
    # Get highly-rated films (rating >= 8)
    highly_rated = Review.objects.filter(
        user=user,
        rating__gte=8
    ).select_related('film').order_by('-rating')[:10]  # Top 10 to avoid too many API calls
    
    if not highly_rated:
        # Fallback: return empty list or popular movies
        return []
    
    # Get user's existing films (to filter out)
    user_film_ids = set(
        WatchStatus.objects.filter(user=user).values_list('film__tmdb_id', flat=True)
    )
    
    # Collect similar films
    recommendations = {}  # Use dict to avoid duplicates: {tmdb_id: movie_data}
    
    for review in highly_rated:
        film = review.film
        if not film.tmdb_id:
            continue
        
        # Get similar films from TMDB
        similar = tmdb_get_similar(film.tmdb_id, media_type=film.type)
        
        for movie in similar:
            tmdb_id = movie.get('id')
            
            # Skip if already in user's watchlist or already in recommendations
            if tmdb_id in user_film_ids or tmdb_id in recommendations:
                continue
            
            # Add to recommendations
            recommendations[tmdb_id] = movie
    
    # Convert to list and sort by TMDB rating (vote_average)
    rec_list = list(recommendations.values())
    rec_list.sort(key=lambda x: x.get('vote_average', 0), reverse=True)
    
    return rec_list[:limit]
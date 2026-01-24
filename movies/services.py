from django.db.models import Avg, Count
from .models import WatchStatus, Review


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
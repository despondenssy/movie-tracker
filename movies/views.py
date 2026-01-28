from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from urllib.parse import urlencode
from .tmdb_client import tmdb_search_movie, tmdb_get_movie_details
from .services_tmdb import import_tmdb_movie
from .services import set_watch_status, get_film_rating_stats
from .models import Film, WatchStatus, Review


def film_detail(request, film_id):
    film = get_object_or_404(Film.objects.prefetch_related("genres"), id=film_id)
    user_watch_status = None
    query = request.GET.get("q", "")
    user_review = None
    tmdb_poster_url = None
    tmdb_rating = None
    tmdb_vote_count = None

    avg_rating, rating_count = get_film_rating_stats(film=film)

    # Pull extra data from TMDB (poster, external rating)
    if film.tmdb_id:
        media_type = "movie"
        if film.type == Film.TypeChoices.SERIES:
            media_type = "tv"
        try:
            tmdb_data = tmdb_get_movie_details(tmdb_id=film.tmdb_id, media_type=media_type)
            poster_path = tmdb_data.get("poster_path")
            if poster_path:
                tmdb_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            tmdb_rating = tmdb_data.get("vote_average")
            tmdb_vote_count = tmdb_data.get("vote_count")
        except Exception:
            # Fail silently if TMDB is not reachable
            pass

    if request.user.is_authenticated:
        watch_status = WatchStatus.objects.filter(user=request.user, film=film).first()
        user_watch_status = watch_status.status if watch_status else None
        user_review = Review.objects.filter(user=request.user, film=film).first()

    reviews = (
        Review.objects.filter(film=film)
        .select_related("user")
        .order_by("-updated_at")
        [:20]
    )

    recommendations = (
        Film.objects.filter(genres__in=film.genres.all())
        .exclude(id=film.id)
        .distinct()
        .prefetch_related("genres")
        .annotate(avg_rating=Avg("reviews__rating"))
        .order_by("-avg_rating", "-id")[:8]
    )

    return render(
        request,
        "movies/film_detail.html",
        {
            "film": film,
            "user_watch_status": user_watch_status,
            "user_review": user_review,
            "avg_rating": avg_rating,
            "rating_count": rating_count,
            "tmdb_poster_url": tmdb_poster_url,
            "tmdb_rating": tmdb_rating,
            "tmdb_vote_count": tmdb_vote_count,
            "reviews": reviews,
            "recommendations": recommendations,
            "query": query,
        },
    )


@require_POST
@login_required
def set_film_status(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    status = request.POST.get("status")
    query = request.POST.get("query", "")

    valid_statuses = {choice for choice, _ in WatchStatus.Status.choices}
    if status not in valid_statuses:
        messages.error(request, "Invalid status")
        return redirect("film_detail", film_id=film.id)

    set_watch_status(user=request.user, film=film, status=status)
    messages.success(request, f"Updated status: {status.title()}")

    if query:
        return redirect(f"/films/{film.id}/?{urlencode({'q': query})}")
    return redirect("film_detail", film_id=film.id)


@require_POST
@login_required
def upsert_review(request, film_id):
    film = get_object_or_404(Film, id=film_id)
    query = request.POST.get("query", "")
    rating_raw = request.POST.get("rating")
    text = (request.POST.get("text") or "").strip()

    try:
        rating = int(rating_raw)
    except (TypeError, ValueError):
        messages.error(request, "Please choose a rating from 1 to 10.")
        if query:
            return redirect(f"/films/{film.id}/?{urlencode({'q': query})}")
        return redirect("film_detail", film_id=film.id)

    if rating < 1 or rating > 10:
        messages.error(request, "Rating must be between 1 and 10.")
        if query:
            return redirect(f"/films/{film.id}/?{urlencode({'q': query})}")
        return redirect("film_detail", film_id=film.id)

    Review.objects.update_or_create(
        user=request.user,
        film=film,
        defaults={"rating": rating, "text": text},
    )

    messages.success(request, "Your review has been saved.")
    if query:
        return redirect(f"/films/{film.id}/?{urlencode({'q': query})}")
    return redirect("film_detail", film_id=film.id)

def search_movies(request):
    query = request.GET.get("q")
    results = []

    if query:
        tmdb_results = tmdb_search_movie(query)
        
        # Добавляем информацию о том, есть ли фильм в БД и его статус у пользователя
        for movie in tmdb_results:
            tmdb_id = movie.get('id')
            try:
                film = Film.objects.get(tmdb_id=tmdb_id)
                movie['in_database'] = True
                movie['film_id'] = film.id
                
                # Проверяем статус у текущего пользователя
                if request.user.is_authenticated:
                    watch_status = WatchStatus.objects.filter(
                        user=request.user,
                        film=film
                    ).first()
                    movie['user_status'] = watch_status.status if watch_status else None
                else:
                    movie['user_status'] = None
            except Film.DoesNotExist:
                movie['in_database'] = False
                movie['film_id'] = None
                movie['user_status'] = None
        
        results = tmdb_results

    context = {
        "query": query,
        "results": results,
    }
    return render(request, "movies/search_movies.html", context)


@require_POST
@login_required
def quick_add_movie(request):
    """Быстрое добавление фильма со статусом из поиска"""
    tmdb_id = request.POST.get("tmdb_id")
    media_type = request.POST.get("media_type")
    status = request.POST.get("status")
    query = request.POST.get("query", "")

    if not tmdb_id or not media_type or not status:
        messages.error(request, "Missing required data")
        return redirect("search_movies")

    # Проверяем, есть ли фильм в БД
    try:
        film = Film.objects.get(tmdb_id=tmdb_id)
    except Film.DoesNotExist:
        # Если нет - импортируем из TMDB
        tmdb_data = tmdb_get_movie_details(
            tmdb_id=tmdb_id,
            media_type=media_type
        )
        film = import_tmdb_movie(tmdb_data)

    # Устанавливаем статус
    set_watch_status(user=request.user, film=film, status=status)
    
    messages.success(request, f"'{film.title}' added to {status}!")
    
    # Возвращаемся на поиск с сохранением запроса
    return redirect(f"/movies/search/?q={query}")


@require_POST
def add_movie(request):
    """Добавление фильма в БД (без статуса) - для детальной страницы"""
    tmdb_id = request.POST.get("tmdb_id")
    media_type = request.POST.get("media_type")
    query = request.POST.get("query", "")

    if not tmdb_id or not media_type:
        return redirect("search_movies")

    tmdb_data = tmdb_get_movie_details(
        tmdb_id=tmdb_id,
        media_type=media_type
    )

    film = import_tmdb_movie(tmdb_data)

    # Редирект на детальную страницу фильма
    if query:
        return redirect(f"/films/{film.id}/?{urlencode({'q': query})}")
    return redirect("film_detail", film_id=film.id)
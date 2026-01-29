from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg, Count
from .forms import SignUpForm
from .models import User
from movies.models import WatchStatus, Review, Film
from movies.tmdb_client import tmdb_get_trending, tmdb_get_popular


def home(request):
    """Dashboard for authenticated users, landing for guests"""
    if not request.user.is_authenticated:
        return render(request, "home.html", {'show_landing': True})
    
    # Quick stats
    watching_count = WatchStatus.objects.filter(user=request.user, status=WatchStatus.Status.WATCHING).count()
    planned_count = WatchStatus.objects.filter(user=request.user, status=WatchStatus.Status.PLANNED).count()
    watched_count = WatchStatus.objects.filter(user=request.user, status=WatchStatus.Status.WATCHED).count()
    
    # Get trending from TMDB
    trending = tmdb_get_trending(media_type="all", time_window="week")[:12]
    
    # Get popular movies from TMDB
    popular = tmdb_get_popular(media_type="movie")[:12]
    
    # Check which films are already in user's database
    if trending:
        trending_ids = [item.get('id') for item in trending]
        user_films = {
            ws.film.tmdb_id: ws.status 
            for ws in WatchStatus.objects.filter(user=request.user, film__tmdb_id__in=trending_ids).select_related('film')
        }
        for item in trending:
            item['user_status'] = user_films.get(item.get('id'))
    
    if popular:
        popular_ids = [item.get('id') for item in popular]
        user_films_pop = {
            ws.film.tmdb_id: ws.status 
            for ws in WatchStatus.objects.filter(user=request.user, film__tmdb_id__in=popular_ids).select_related('film')
        }
        for item in popular:
            item['user_status'] = user_films_pop.get(item.get('id'))
    
    context = {
        'watching_count': watching_count,
        'planned_count': planned_count,
        'watched_count': watched_count,
        'trending_films': trending,
        'popular_films': popular,
    }
    
    return render(request, "home.html", context)


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile(request, username=None):
    """User profile with statistics"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    # Get counts for each status
    planned_count = WatchStatus.objects.filter(user=user, status=WatchStatus.Status.PLANNED).count()
    watching_count = WatchStatus.objects.filter(user=user, status=WatchStatus.Status.WATCHING).count()
    watched_count = WatchStatus.objects.filter(user=user, status=WatchStatus.Status.WATCHED).count()
    dropped_count = WatchStatus.objects.filter(user=user, status=WatchStatus.Status.DROPPED).count()
    
    # Get user's average rating
    user_reviews = Review.objects.filter(user=user)
    avg_rating = user_reviews.aggregate(avg=Avg('rating'))['avg']
    reviews_count = user_reviews.count()
    
    context = {
        'profile_user': user,
        'is_own_profile': user == request.user,
        'planned_count': planned_count,
        'watching_count': watching_count,
        'watched_count': watched_count,
        'dropped_count': dropped_count,
        'total_count': planned_count + watching_count + watched_count + dropped_count,
        'avg_rating': avg_rating,
        'reviews_count': reviews_count,
    }
    
    return render(request, 'users/profile.html', context)


@login_required
def watchlist(request, status):
    """Display user's watchlist by status"""
    valid_statuses = {choice for choice, _ in WatchStatus.Status.choices}
    if status not in valid_statuses:
        messages.error(request, "Invalid status")
        return redirect('profile')
    
    films = WatchStatus.objects.filter(
        user=request.user,
        status=status
    ).select_related('film').prefetch_related('film__genres').order_by('-updated_at')
    
    # Get user's reviews for these films
    film_ids = [ws.film.id for ws in films]
    user_reviews = {
        review.film_id: review 
        for review in Review.objects.filter(user=request.user, film_id__in=film_ids)
    }
    
    context = {
        'status': status,
        'status_display': dict(WatchStatus.Status.choices)[status],
        'watchlist_items': films,
        'user_reviews': user_reviews,
    }
    
    return render(request, 'users/watchlist.html', context)
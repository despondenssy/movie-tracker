from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms import ValidationError


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class Film(models.Model):
    class TypeChoices(models.TextChoices):
        MOVIE = "movie", "Movie"
        SERIES = "series", "Series"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    tmdb_id = models.PositiveIntegerField(unique=True, null=True, blank=True)

    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(null=True, blank=True)

    type = models.CharField(
        max_length=10,
        choices=TypeChoices.choices,
        default=TypeChoices.MOVIE
    )
    genres = models.ManyToManyField(Genre, related_name="films")

    def clean(self):
        if self.end_year and self.end_year < self.start_year:
            raise ValidationError("end_year cannot be less than start_year")

    def __str__(self):
        # Фильмы
        if self.type == self.TypeChoices.MOVIE:
            return f"{self.title} ({self.start_year})"

        # Сериалы
        if self.end_year:
            if self.start_year == self.end_year:  # мини-сериал
                years = f"{self.start_year}"
            else:
                years = f"{self.start_year}–{self.end_year}"
        else:
            years = f"{self.start_year}–…"

        return f"{self.title} ({years})"
    

class WatchStatus(models.Model):

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        WATCHING = "watching", "Watching"
        WATCHED = "watched", "Watched"
        DROPPED = "dropped", "Dropped"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="watchlist"
    )

    film = models.ForeignKey(
        "movies.Film",
        on_delete=models.CASCADE,
        related_name="watchers"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "film")

    def __str__(self):
        return f"{self.user} → {self.film} ({self.status})"
    

class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    film = models.ForeignKey(
        "movies.Film",
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "film")

    def __str__(self):
        return f"{self.user} → {self.film} ({self.rating})"
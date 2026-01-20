from django.contrib import admin
from .models import Film, Genre, Review, WatchStatus

admin.site.register(Genre)
admin.site.register(Film)
admin.site.register(WatchStatus)
admin.site.register(Review)
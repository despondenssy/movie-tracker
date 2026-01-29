from django.urls import path
from django.contrib.auth import views as auth_views
from .views import home, signup, profile, watchlist

urlpatterns = [
    path("", home, name="home"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", signup, name="signup"),
    path("profile/", profile, name="profile"),
    path("profile/<str:username>/", profile, name="profile_user"),
    path("watchlist/<str:status>/", watchlist, name="watchlist"),
]
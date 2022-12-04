from django.urls import path
from . import views
urlpatterns = [
    path("videos/", views.popular_videos),
    path("bubbles/", views.bubbles),
    path("emotions/", views.emotions)
]
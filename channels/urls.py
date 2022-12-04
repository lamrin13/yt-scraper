from django.urls import path
from . import views
urlpatterns = [
    path("channel_id/", views.get_channel_id),
    path("channel_stat/", views.channel_stat),
    path("comments/",views.get_comments)
]
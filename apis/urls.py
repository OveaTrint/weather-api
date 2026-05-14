from django.urls import path

from .views import get_weather, root

urlpatterns = [
    path("", root),
    path("weather/<str:location>", get_weather),
]

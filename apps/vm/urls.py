from django.urls import path
from apps.vm import views

urlpatterns = [
    path(
        "flavors/",
        views.FlavorListView.as_view(),
        name="flavors",
    ),
    path(
        "images/",
        views.ImageListView.as_view(),
        name="images",
    ),
    path(
        "networks/",
        views.NetworkListView.as_view(),
        name="networks",
    ),
    path(
        "servers/",
        views.ServerListCreateView.as_view(),
        name="servers",
    ),
]

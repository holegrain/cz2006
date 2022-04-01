from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    SearchView, AdvSearchView
)

app_name = 'search'

urlpatterns = [
    path('', SearchView, name='search'),
    path('adv/', AdvSearchView, name='advsearch'),
]
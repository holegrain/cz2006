from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    SearchView, AdvSearchView, ResultView
)

app_name = 'search'

urlpatterns = [
    path('', SearchView, name='search'),
    path('adv/', AdvSearchView, name='advsearch'),
    path('<int:id>/', ResultView, name='result'),
]
from django.urls import path
from django.contrib.auth import views as auth_views

from books.models import Rate
from .views import (
    ViewBook,
    RateBook,
    SaveBook,
)

app_name = 'accounts'
urlpatterns = [
    path(r'^viewbook/(?P<bid>.*)/$', ViewBook, name='viewbook'),
    path('ratebook/', RateBook, name='ratebook'),
    path('savebook/', SaveBook, name='savebook'),
]
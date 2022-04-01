from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    ViewBook,
    RateBook,
    SaveBook,
)

app_name = 'books'

urlpatterns = [
    path('<int:bid>/', ViewBook, name='ViewBook'),
    path('ratebook/', RateBook, name='ratebook'),
    path('savebook/', SaveBook, name='savebook'),
]
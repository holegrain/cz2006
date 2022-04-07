from django.urls import path
from .views import (
    ViewBook,
    SaveBook,
)

app_name = 'books'

urlpatterns = [
    path('<int:bid>/', ViewBook, name='ViewBook'),
    path('savebook/', SaveBook, name='SaveBook'),
]
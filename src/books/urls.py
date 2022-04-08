from django.urls import path
from .views import (
    ViewBook,
)

app_name = 'books'

urlpatterns = [
    path('<int:bid>/', ViewBook, name='ViewBook'),
]
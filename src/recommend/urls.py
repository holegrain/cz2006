from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    ResultView
)

app_name = 'recommend'

urlpatterns = [
    path('<int:id>/', ResultView, name='result'),
]
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    ResultView, Recommend
)

app_name = 'recommend'

urlpatterns = [
    path('recommend/', Recommend, name='recommend'),
    path('<int:id>/', ResultView, name='result'),
]
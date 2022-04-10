from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    ResultView1, Recommend
)

app_name = 'recommend'

urlpatterns = [
    path('', Recommend, name='recommend'),
    path('<int:id>/', ResultView1, name='result1'),
]
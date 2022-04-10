from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    SearchView, 
    AdvSearchView, 
    ResultView,
    ResultTitleView,
    ResultNewestView,
    ResultOldestView,
    ResultPopularityView

)

app_name = 'search'

urlpatterns = [
    path('', SearchView, name='search'),
    path('adv/', AdvSearchView, name='advsearch'),
    path('<int:id>/', ResultView, name='result'),
    path('<int:id>/sortby=title', ResultTitleView, name='bytitle'),
    path('<int:id>/sortby=newest', ResultNewestView, name='bynewest'),
    path('<int:id>/sortby=oldest', ResultOldestView, name='byoldest'),
    path('<int:id>/sortby=popularity', ResultPopularityView, name='bypopularity')

]
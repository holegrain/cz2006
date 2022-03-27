from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    SignupView,
    SettingsView,
    AccountView,
    ProfileView,
    DeleteView,
    LoginView,
)

app_name = 'accounts'
urlpatterns = [
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', SignupView, name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('settings/', SettingsView, name='settings'),
    path('', AccountView, name='myaccount'),
    path('editprofile/', ProfileView, name='profile'),
    path('delete/', DeleteView, name='delete'),
]
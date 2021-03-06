from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    SignupView,
    AccountView,
    ProfileView,
    DeleteView,
    LoginView,
    ForgetPwView
)

app_name = 'accounts'
urlpatterns = [
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', SignupView, name='signup'),
    path('login/', LoginView, name='login'),
    path('', AccountView, name='myaccount'),
    path('editprofile/', ProfileView, name='profile'),
    path('delete/', DeleteView, name='delete'),
    path('forget/', ForgetPwView, name='forget')
]
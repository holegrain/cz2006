from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserSignupForm, UserUpdateForm
from .models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, get_user_model

# Create your views here.
def SignupView(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Your account has been created. You can log in now!')
            return redirect('/')
    else:
        form = UserSignupForm()
    context = {'form': form}
    return render(request, 'signup.html', context)

class LoginView(LoginView):
    template_name = 'login.html'
    next_page = '/'

def SettingsView(request):
    return render(request, 'settings.html')

def AccountView(request):
    return render(request, 'account.html')

@login_required(login_url='/account/login/')
def ProfileView(request):
    user = request.user
    obj = get_object_or_404(User, username=user)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, initial={'dob': obj.dob, 'email': obj.email}, request=request, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Your account successfully updated.')
            form = UserUpdateForm(initial={'username': obj.username, 'dob': obj.dob, 'email': obj.email}, request=request)
    else:
        form = UserUpdateForm(initial={'username': obj.username, 'dob': obj.dob, 'email': obj.email}, request=request)

    context = {'form': form,
    'object': obj}
    return render(request, 'profile.html', context)

def DeleteView(request):
    return render(request, 'delete.html')
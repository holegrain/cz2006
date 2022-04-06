from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserSignupForm, UserUpdateForm, UserLoginForm, UserDeleteForm, ForgetPWForm
from .models import User
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout
import datetime
from .utils import random_password

def ForgetPwView(request):
    if request.method == 'POST':
        form = ForgetPWForm(request.POST)
        if form.is_valid():
            entry = form.cleaned_data['entry']
            if '@' in entry:
                user = User.objects.filter(email=entry).first()
            else: 
                user = User.objects.filter(username=entry).first()

            if isinstance(user, User): 
            # if there is a valid username email pair
                new_pw = random_password()
                user.set_password(new_pw)
                user.save()
                send_mail(
                    subject = 'Reset password',
                    message = "Dear {0},\nOur journey to find great books begins today. \nYou have requested to rest your password on klib. Here is your new password \n{1} \nPlease change your password as soon as possible. \nIf you did not make this request, please email us at st.test1998@gmail.com \nRegards, \nThe klib team.".format(user.username, new_pw),
                    from_email = 'st.test1998@gmail.com',
                    recipient_list = [user.email],
                    fail_silently=False,
                )
                # go back to account page
                messages.success(
                    request, f'We have emailed you your temporary password. You can log in now!')
                return render(request, 'login.html')
            
            else: 
                messages.error(
                    request, f'No user found')
    else:   
        form = ForgetPWForm()
    context = {'form': form}
    return render(request, 'forget.html', context)

# Create your views here.
def SignupView(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST, initial={'dob': datetime.date.today()})
        if form.is_valid():
            send_mail(
                'Welcome to klib!',
                f"Thank you {form.cleaned_data['username']}, our journey to find great books begins today!",
                'st.test1998@gmail.com',
                [form.cleaned_data['email']],
                fail_silently=False,
            )
            form.save()
            messages.success(
                request, f'Your account has been created. You can log in now!')
            return redirect('/account/login/')
    else:
        form = UserSignupForm(initial={'dob': datetime.date.today()})
    context = {'form': form}
    return render(request, 'signup.html', context)

        
def LoginView(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            entry = form.cleaned_data.get('entry')
            password = form.cleaned_data.get('password')
            if '@' in entry:
                user = User.objects.get(email=entry)
                user = authenticate(username=user, password=password)
            else:
                user = authenticate(username=entry, password=password)
            if user == None:
                messages.error(request, f"Your username and password didn't match. Please try again!")
            else:
                login(request, user)
                request.session['is_logged'] = True
                user = request.user.id
                request.session['user_id'] = user
                return redirect('/')
    else: 
        form = UserLoginForm()
    context = {'form': form}
    return render(request, 'login.html', context)

def AccountView(request):
    return render(request, 'account.html')

@login_required(login_url='/account/login/')
def ProfileView(request):
    user = request.user
    obj = get_object_or_404(User, username=user)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, initial={'dob': obj.dob, 'email': obj.email}, request=request)
        if form.is_valid():
            obj.dob = form.cleaned_data.get('dob')
            obj.email = form.cleaned_data.get('email')
            if form.cleaned_data.get('password') != None:
                obj.set_password(form.cleaned_data.get('password'))
            obj.save()
            messages.success(
                request, f'Your account successfully updated.')
            form = UserUpdateForm(initial={'username': obj.username, 'dob': obj.dob, 'email': obj.email}, request=request)
    else:
        form = UserUpdateForm(initial={'username': obj.username, 'dob': obj.dob, 'email': obj.email}, request=request)
    context = {'form': form,
    'object': obj}
    return render(request, 'profile.html', context)

@login_required(login_url='/account/login/')
def DeleteView(request):
    if request.method == 'POST':
        form = UserDeleteForm(request.POST, request=request)
        if form.is_valid():
            obj = get_object_or_404(User, username=request.user)
            logout(request)
            obj.delete()
            return redirect('/') 
    else:
        form = UserDeleteForm(request=request)
    context = {'form': form}
    return render(request, 'delete.html', context)
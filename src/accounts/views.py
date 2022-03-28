from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserSignupForm, UserUpdateForm, UserLoginForm, UserDeleteForm, ForgetPWForm
from .models import User
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout
from .utils import random_password

def ForgetPwView(request):
    if request.method == 'POST':
        form = ForgetPWForm(request.POST)
        if form.is_valid():
            # get the relevant field first
            name = form.cleaned_data['username']
            email = form.cleaned_data['email']
            # check the email and username
            user = get_object_or_404(User, username=name, email=email)

            if isinstance(user, User): # if there is a valid username email pair
                new_pw = random_password()
                user.password = new_pw
                send_mail(
                    'Reset password',
                    f"Dear {name}, our journey to find great books begins today\
                        you have requested to rest your password on klib. Here is your new password \
                            {new_pw} \
                        if you did not make this request, please email us at st.test1998@gmail.com \
                      Regards, \
                      The klib team.",
                    'st.test1998@gmail.com',
                    [form.cleaned_data['email']],
                    fail_silently=False,
                )
                # go back to account page
                return render(request, 'login.html')
            
            else: # if invalid username
                # TODO @xiangyi: display error message? Need someone else to implement I don't know how
                context = {'error': "wrong username and password you dumbfuck."}
                render(request, 'forget.html', context)
    else:   
        form = ForgetPWForm()
    context = {'form': form}
    return render(request, 'forget.html', context)

# Create your views here.
def SignupView(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
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
        form = UserSignupForm()
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
                obj.set_password(form.clean_password2())
            obj.save()
            messages.success(
                request, f'Your account successfully updated.')
            form = UserUpdateForm(initial={'username': obj.username, 'dob': obj.dob, 'email': obj.email}, request=request)
    else:
        form = UserUpdateForm(initial={'username': obj.username, 'dob': obj.dob, 'email': obj.email}, request=request)
    context = {'form': form,
    'object': obj}
    return render(request, 'profile.html', context)

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
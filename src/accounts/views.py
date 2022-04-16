from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserSignupForm, UserUpdateForm, UserLoginForm, UserDeleteForm, ForgetPWForm
from .models import User
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from nlbsg import Client
from nlbsg.catalogue import PRODUCTION_URL
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
import datetime
from books.models import Save, View
from star_ratings.models import UserRating
from .utils import random_password

API_KEY = 'RGV2LVpob3VXZWk6IW5sYkAxMjMj'
client = Client(PRODUCTION_URL, API_KEY)


def ForgetPwView(request):
    # check if user is authenticated
    if request.user.is_authenticated:
        return render (request, 'loggedin.html')
    if request.method == 'POST':
        form = ForgetPWForm(request.POST)
        if form.is_valid():
            entry = form.cleaned_data['entry']
            #  check for username or email
            if '@' in entry:
                user = User.objects.filter(email=entry).first()
            else: 
                user = User.objects.filter(username=entry).first()

            if isinstance(user, User): # if user exists
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
                # redirect to account page
                messages.success(
                    request, f'Check your email for a temporary password.')
                return redirect('/account/login/')
            
            else: 
                messages.error(
                    request, f'No user found')
    else:   
        form = ForgetPWForm()
    context = {'form': form}
    return render(request, 'forget.html', context)


def SignupView(request):
    # check if user is authenticated
    if request.user.is_authenticated:
        return render (request, 'loggedin.html')
    if request.method == 'POST':
        form = UserSignupForm(request.POST, initial={'dob': datetime.date.today()})
        if form.is_valid():
            # no validation error raised, to store object in database
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
            # redirect to login page
            return redirect('/account/login/')
    else:
        form = UserSignupForm(initial={'dob': datetime.date.today()})
    context = {'form': form}
    return render(request, 'signup.html', context)

        
def LoginView(request):
    # check if user is authenticated
    if request.user.is_authenticated:
        return render (request, 'loggedin.html')
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            entry = form.cleaned_data.get('entry')
            password = form.cleaned_data.get('password')
            # check for username of email
            if '@' in entry:
                user = User.objects.get(email=entry)
                user = authenticate(username=user, password=password)
            else:
                user = authenticate(username=entry, password=password)
            # authentication failed
            if user == None:
                messages.error(request, f"Your username/email and password didn't match.")
            # authentication passed
            else:
                # create session 
                login(request, user)
                request.session['is_logged'] = True
                user = request.user.id
                request.session['user_id'] = user
                return redirect('/')
    else: 
        form = UserLoginForm()
    context = {'form': form}
    return render(request, 'login.html', context)


# decorator for login required
@login_required(login_url='/account/login/')
def AccountView(request):
    # get saved books
    saveobjs = Save.objects.filter(user=request.user)
    # get viewed books
    try:
        viewobjs = View.objects.filter(user=request.user).order_by('-lastviewed')[:20]
    except:
        viewobjs = View.objects.filter(user=request.user)
    # get rated books
    rateobjs = UserRating.objects.filter(user=request.user)
    viewbooklist = []
    savebooklist = []
    ratebooklist = []
    # get titles of books
    for i in rateobjs:
        book = client.get_title_details(bid=i.rating.content_object.bid).title_detail
        if book != None:
            ratebooklist.append(book)
    for i in viewobjs:
        book = client.get_title_details(bid=i.bid).title_detail
        if book != None:
            viewbooklist.append(book)
    for i in saveobjs:
        book = client.get_title_details(bid=i.bid).title_detail
        if book != None:
            savebooklist.append(book)

    context = {
        'save': savebooklist,
        'view': viewbooklist,
        'rate': ratebooklist
    }
    return render(request, 'account.html', context)


# decorator for login required
@login_required(login_url='/account/login/')
def ProfileView(request):
    user = request.user
    obj = get_object_or_404(User, username=user)
    if request.method == 'POST':
        # display user's dob and email
        form = UserUpdateForm(request.POST, initial={'dob': obj.dob, 'email': obj.email}, request=request)
        if form.is_valid(): # if user is authenticated and no validation errors are raised
            obj.dob = form.cleaned_data.get('dob')
            obj.email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            # if new password is entered, set new password
            if password != '':
                obj.set_password(password)
            obj.save()
            messages.success(
                request, f'Your account is successfully updated.')
            form = UserUpdateForm(initial={'username': obj.username, 'dob': obj.dob, 'email': obj.email}, request=request)
    else:
        form = UserUpdateForm(initial={'username': obj.username, 'dob': obj.dob, 'email': obj.email}, request=request)
    context = {'form': form,
    'object': obj}
    return render(request, 'profile.html', context)


# decorator for login required
@login_required(login_url='/account/login/')
def DeleteView(request):
    if request.method == 'POST':
        form = UserDeleteForm(request.POST, request=request)
        if form.is_valid(): # if user is authenticated
            obj = get_object_or_404(User, username=request.user)
            # delete user related data
            Save.objects.filter(user=request.user).delete()
            View.objects.filter(user=request.user).delete()
            UserRating.objects.filter(user=request.user).delete()
            # logout
            logout(request)
            # delete user from database
            obj.delete() 
            return redirect('/') 
    else:
        form = UserDeleteForm(request=request)
    context = {'form': form}
    return render(request, 'delete.html', context)
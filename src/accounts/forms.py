from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model, authenticate
from .models import User
from django.db import transaction

years = [x for x in range(1920, 2023)]

class ForgetPWForm(forms.Form):
    username = forms.CharField(min_length=6, max_length = 256)
    email = forms.CharField(min_length=6, max_length = 256)


class UserSignupForm(UserCreationForm):
    dob = forms.DateField(widget=forms.SelectDateWidget(years=years))
    email = forms.CharField(min_length=6, max_length = 256)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'dob']

    # validate username
    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username=username)
        if qs.exists():
            raise forms.ValidationError("Username is taken")
        elif not username.isalnum():
            raise forms.ValidationError("Username should only contain letters and numbers.")
        elif len(username)<4:
            raise forms.ValidationError("Username is too short")
        elif len(username)>32:
            raise forms.ValidationError("Username is too long")
        return username

    # validate email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("Email already has an account.")
        return email

class UserLoginForm(forms.Form):
    entry = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'Email/Username', 
        'style':'position: relative;bottom:40px;margin:10px 0;', 
        'class':'form-control'}))
    password = forms.CharField(max_length=32, widget=forms.PasswordInput(attrs={
        'placeholder':'Password', 
        'style':'position: relative;bottom:40px;margin:10px 0;', 
        'class':'form-control'}))

    #validate password:
    def clean_entry(self):
        entry = self.cleaned_data.get('entry')
        if '@' in entry:
            qs = User.objects.filter(email=entry)
            if not qs.exists():
                raise forms.ValidationError("Email does not exist.")
        else: 
            qs = User.objects.filter(username=entry)
            if not qs.exists():
                raise forms.ValidationError("Username does not exist.")
        return entry


class UserUpdateForm(UserCreationForm):
    dob = forms.DateField(widget=forms.SelectDateWidget(years=years))
    email = forms.CharField(min_length=6, max_length = 256)
    password1 = forms.CharField(max_length=32, label='new password',widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(max_length=32, label='password confirmation',widget=forms.PasswordInput, required=False)
    current = forms.CharField(max_length=32, label='current password', widget=forms.PasswordInput)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['email', 'password1', 'password2', 'dob']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(UserUpdateForm, self).__init__(*args, **kwargs)

    #validate password:
    def clean_current(self):
        current = self.cleaned_data.get('current')
        if authenticate(username=self.request.user, password=current) == None:
            raise forms.ValidationError("Incorrect Password.")
        return current

     # validate username
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username.isalnum():
            raise forms.ValidationError("Username should only contain letters and numbers.")
        elif len(username)<4:
            raise forms.ValidationError("Username is too short")
        elif len(username)>32:
            raise forms.ValidationError("Username is too long")
        return username

    # validate email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        user = self.request.user
        if email != user.email:
            qs = User.objects.filter(email=email)
            if qs.exists():
                raise forms.ValidationError("Email already has an account.")
        return email


class UserDeleteForm(forms.Form):
    password = forms.CharField(max_length=32, label='password', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(UserDeleteForm, self).__init__(*args, **kwargs)


    #validate password:
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if authenticate(username=self.request.user, password=password) == None:
            raise forms.ValidationError("Incorrect Password.")
        return password

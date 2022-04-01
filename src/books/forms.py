from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model, authenticate
from .models import User
from django.db import transaction

'''
For more information, visit:
https://stackoverflow.com/questions/59593884/django-rendering-a-number-as-a-5-stars-rating
'''

class RatingForm(forms.Form):
    rating = forms.IntegerField(min_value=1, max_value=5)
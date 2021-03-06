from django.db import models
import datetime
from django.forms import ValidationError
from django.contrib.auth.models import (
 AbstractUser, UserManager
)

# validate date
def validate_date(date):
    if date > datetime.date.today():
        raise ValidationError("Date cannot be in the future")

# user model which extends AbstractUser
class User(AbstractUser):
    dob = models.DateField(null = True, validators=[validate_date])
    objects = UserManager()

    USERNAME_FIELD = 'username'
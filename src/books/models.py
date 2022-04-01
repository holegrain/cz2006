from django.db import models
from accounts.models import User

# The Rate() model stores the rating of books.
class Rate(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    bid = models.CharField(max_length=9)
    rating = models.IntegerField()

# The View() model stores the books viewed by the user.
class View(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    bid = models.CharField(max_length=9)
    # auto_now and auto_now_add are not recommended.
    # Any field with the auto_now attribute set will also inherit editable=False and therefore will not show up in the admin panel.
    lastviewed=models.DateTimeField()

# The Save() model stores the books saved by the user.
class Save(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    bid = models.CharField(max_length=9)

# The Book() model stores the book bid.
class Book(models.Model):
    bid = models.CharField(max_length=9)
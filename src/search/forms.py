from django import forms
'''
class RegexValidator(regex=None, message=None, code=None, inverse_match=None, flags=0)
A RegexValidator searches the provided value for a given regular expression with re.search(). 
By default, raises a ValidationError with message and code if a match is not found.
For more information visit:
https://docs.djangoproject.com/en/4.0/ref/validators/#regexvalidator 
'''
from django.core.validators import RegexValidator

alphanumeric = RegexValidator('^[a-zA-Z0-9 ]*$', message="Only letters and numbers are allowed.")
onlyX = RegexValidator('^[X0-9]*$', message="Only numbers and capital 'X' are allowed.")
withcomma = RegexValidator('^[a-zA-Z0-9 ,]*$', message="Only letters and numbers are allowed.")

'''
https://stackoverflow.com/questions/15472764/regular-expression-to-allow-spaces-between-words
'''


class SimpleSearchForm(forms.Form):
    title = forms.CharField(max_length=50, label='Title', required=False, validators=[alphanumeric])
    author = forms.CharField(max_length=50, label='Author', required=False, validators=[alphanumeric])
    isbn = forms.CharField(max_length=13, label='ISBN', required=False, validators=[onlyX])
    bid = forms.CharField(max_length=9, label='BID', required=False)
    # TODO: Are we gonna allow tagging? Or we split the genres by ' ' and then group as a tuple.
    genres = forms.CharField(max_length=50, label='Genre(s)', help_text="Please seperate multiple genres using commas.", required=False, validators=[withcomma]) 
    
    def clean(self):
        # TODO: Hide validation error for erroneous input.
        if not (self.cleaned_data.get('title') or self.cleaned_data.get('author') or self.cleaned_data.get('isbn') or self.cleaned_data.get('bid') or self.cleaned_data.get('genres')):
            raise forms.ValidationError("Please fill in at least one of the fields to begin searching.")

    def clean_bid(self):
        bid = self.cleaned_data.get('bid')
        if bid:
            if not bid.isnumeric():
                raise forms.ValidationError("BID should only contain numbers.")
            return bid

class AdvancedSearchForm(forms.Form):
    keywords = forms.CharField(max_length=50, label='Keyword(s)', help_text="Please seperate multiple genres using commas.", required=False, validators=[withcomma])
    plot = forms.CharField(max_length=1000, label='Plot', required=False)
    
    # TODO: Hide validation error for erroneous input.
    def clean(self):
        if not (self.cleaned_data.get('keywords') or self.cleaned_data.get('plot')):
            raise forms.ValidationError("Please fill in at least one of the fields to begin searching.")


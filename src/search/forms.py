from django import forms
'''
class RegexValidator(regex=None, message=None, code=None, inverse_match=None, flags=0)
A RegexValidator searches the provided value for a given regular expression with re.search(). 
By default, raises a ValidationError with message and code if a match is not found.
For more information visit:
https://docs.djangoproject.com/en/4.0/ref/validators/#regexvalidator 
'''
from django.core.validators import RegexValidator

alphanumeric = RegexValidator(
    '^[a-zA-Z0-9 ]*$', message="Only letters and numbers are allowed.")
onlyX = RegexValidator(
    '^[X0-9]*$', message="Only numbers and capital 'X' are allowed.")
withcomma = RegexValidator(
    '^[a-zA-Z0-9 ,]*$', message="Only letters and numbers are allowed.")

'''
https://stackoverflow.com/questions/15472764/regular-expression-to-allow-spaces-between-words
'''


class SimpleSearchForm(forms.Form):
    title = forms.CharField(max_length=50, label='Title', required=False, validators=[alphanumeric],
                            widget=forms.TextInput(attrs={
                                'class': 'form-input'}))
    author = forms.CharField(max_length=50, label='Author', required=False, validators=[alphanumeric],
                             widget=forms.TextInput(attrs={
                                 'class': 'form-input'}))
    isbn = forms.CharField(max_length=13, label='ISBN', required=False, validators=[onlyX],
                           widget=forms.TextInput(attrs={
                               'class': 'form-input'}))
    # TODO: Are we gonna allow tagging? Or we split the genres by ' ' and then group as a tuple.
    genres = forms.CharField(max_length=50, label='Genre(s)',
                             help_text="Please seperate genres using only a single comma.", required=False, validators=[withcomma],
                             widget=forms.TextInput(attrs={
                                 'placeholder': 'romance, mystery, horror (separate with comma)',
                                 'class': 'form-input'}))

    def clean(self):
        # TODO: Hide validation error for erroneous input.
        if not (self.cleaned_data.get('title') or self.cleaned_data.get('author') or self.cleaned_data.get('isbn') or self.cleaned_data.get('bid') or self.cleaned_data.get('genres')):
            raise forms.ValidationError(
                "Please fill in at least one of the fields to begin searching.")


class AdvancedSearchForm(forms.Form):
    plot = forms.CharField(max_length=1000, label='Plot', required=False,
                               widget=forms.Textarea(attrs={
                               'class': 'form-input',
                               'placeholder': 'Enter Your Plot',
                               'rows': 5,
                                'cols': 90,
                                'maxlength': '1000'}))



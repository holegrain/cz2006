from django import forms

class SimpleSearchForm(forms.Form):
    title = forms.CharField(max_length=50, label='Title', required=False)
    author = forms.CharField(max_length=50, label='Author', required=False)
    isbn = forms.CharField(max_length=13, label='ISBN', required=False)
    bid = forms.CharField(max_length=9, label='BID', required=False)
    # TODO: Are we gonna allow tagging? Or we split the genres by ' ' and then group as a tuple.
    genres = forms.CharField(max_length=50, label='Genre(s)', help_text="Please seperate multiple genres using commas.", required=False) 
    
    def clean(self):
        # TODO: Hide validation error for erroneous input.
        if not (self.cleaned_data.get('title') or self.cleaned_data.get('author') or self.cleaned_data.get('isbn') or self.cleaned_data.get('bid') or self.cleaned_data.get('genres')):
            raise forms.ValidationError("Please fill in at least one of the fields to begin searching.")
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            if not title.isalnum():
                raise forms.ValidationError("Title should only contain letters and numbers.")
            return title

    def clean_author(self):
        author = self.cleaned_data.get('author')
        if author:
            if not author.isalnum():
                raise forms.ValidationError("Author should only contain letters and numbers.")
            return author

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if isbn:
            if not isbn.isalnum():
                raise forms.ValidationError("ISBN should only contain letters and numbers.")
            return isbn

    def clean_bid(self):
        bid = self.cleaned_data.get('bid')
        if bid:
            if not bid.isnumeric():
                raise forms.ValidationError("BID should only contain numbers.")
            return bid

    def clean_genres(self):
        genres = self.cleaned_data.get('genres')
        if genres:
            if not genres.isalpha():
                raise forms.ValidationError("Genres should only contain letters.")
            return genres

class AdvancedSearchForm(forms.Form):
    keywords = forms.CharField(max_length=50, label='Keyword(s)', required=False)
    plot = forms.CharField(max_length=1000, label='Plot', required=False)
    
    # TODO: Hide validation error for erroneous input.
    def clean(self):
        if not (self.cleaned_data.get('keywords') or self.cleaned_data.get('plot')):
            raise forms.ValidationError("Please fill in at least one of the fields to begin searching.")

    def clean_keywords(self):
        keywords = self.cleaned_data.get('keywords')
        if keywords:
            if not keywords.isalnum():
                raise forms.ValidationError("Keywords should only contain letters and numbers.")
            return keywords

    def clean_plot(self):
        plot = self.cleaned_data.get('plot')
        if plot:
            if not plot.isalnum():
                raise forms.ValidationError("Plot should only contain letters and numbers.")
            return plot


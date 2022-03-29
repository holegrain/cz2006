from django.shortcuts import render
from .forms import AdvancedSearchForm, SimpleSearchForm
from .utils import simple_search, adv_search

def SearchView(request):
    if request.method == 'POST':
        form = SimpleSearchForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            author = form.cleaned_data.get('author')
            isbn = form.cleaned_data.get('isbn')
            bid = form.cleaned_data.get('bid')
            genres = form.cleaned_data.get('genres')
            
    else:
        form = SimpleSearchForm()
    context = {'form': form}
    return render(request, 'search.html', context)


def AdvSearchView(request):
    if request.method == 'POST':
        form = AdvancedSearchForm(request.POST)
        if form.is_valid():
            keywords = form.cleaned_data.get('keywords')
            plot = form.cleaned_data.get('plot')
    else: 
        form = AdvancedSearchForm()
    context = {'form': form}
    return render(request, 'advsearch.html', context)

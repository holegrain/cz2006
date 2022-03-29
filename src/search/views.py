from django.shortcuts import render
from .forms import AdvancedSearchForm, SimpleSearchForm
from .utils import standard_search, adv_search
from django.contrib import messages

def SearchView(request):
    if request.method == 'POST':
        form = SimpleSearchForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            isbn = form.cleaned_data.get('isbn')
            author = form.cleaned_data.get('author')
            genres = form.cleaned_data.get('genres')
            genretuple = tuple(genres.split(','))
            resultlist = standard_search(title=title, author=author, isbn=isbn, genre=genretuple)
            if resultlist:
                return render(request, 'booklist.html', {'resultlist': resultlist})
            else:
                messages.error(
                    request, f"Sorry, no matching books can be found!"
                )
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
            resultlist = adv_search(keywords=keywords, plot=plot)
            if resultlist:
                return render(request, 'booklist.html', {'resultlist': resultlist})
            else:
                messages.error(
                    request, f"Sorry, no matching books can be found!"
                )
    else: 
        form = AdvancedSearchForm()
    context = {'form': form}
    return render(request, 'advsearch.html', context)

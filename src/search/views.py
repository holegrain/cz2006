from django.shortcuts import render, redirect
from .forms import AdvancedSearchForm, SimpleSearchForm
from .utils import standard_search, adv_search
from django.http import Http404  
from math import ceil
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
            resultlist, length = standard_search(title=title, author=author, isbn=isbn, genre=genretuple)
            if title:
                search = title+'...'
            elif isbn:
                search = isbn+'...'
            elif author:
                search = author+'...'
            elif isbn:
                search = genres+'...'
            print(search)
            request.session['search'] = search
            request.session['resultlength'] = length
            request.session['resultlist'] = resultlist
            resultlist = request.session['resultlist']
            if resultlist:
                return redirect('http://127.0.0.1:8000/search/1')
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
            plot = form.cleaned_data.get('plot')
            resultlist, length = adv_search(plot=plot)
            plot_truncated = plot[:30] + '...'
            request.session['search'] = plot
            request.session['resultlength'] = length
            request.session['resultlist'] = resultlist
            resultlist = request.session['resultlist']
            if resultlist:
                return redirect('http://127.0.0.1:8000/search/1')
            else:
                messages.error(
                    request, f"Sorry, no matching books can be found!"
                )
    else: 
        form = AdvancedSearchForm()
    context = {'form': form}
    return render(request, 'advsearch.html', context)

def ResultView(request, id=id):
    resultlist = request.session['resultlist']
    length = request.session['resultlength']
    plot = request.session['search']
    start = (id-1)*10 + 1
    if start>length:
        raise Http404  
    end = id*10
    if end>length:
        end=length
    resultlist = resultlist[start:end]
    pagenum = ceil(length/10)
    context = {'resultlist':resultlist, 'page':range(1,pagenum+1), 'plot':plot, 'current':id}
    if resultlist:
         return render(request, 'booklist.html', context)
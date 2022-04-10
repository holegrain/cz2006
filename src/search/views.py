from django.shortcuts import render, redirect
from .forms import AdvancedSearchForm, SimpleSearchForm
from .utils import standard_search, adv_search, filter, sort
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
            genretuple = tuple(genres.split(', '))
            resultlist, length = standard_search(title=title, author=author, isbn=isbn, subject=genretuple)
            if title:
                search = title+'...'
            elif isbn:
                search = isbn+'...'
            elif author:
                search = author+'...'
            elif genres:
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
            try:
                plot_truncated = plot[:30] + '...'
            except:
                plot_truncated=plot
            request.session['search'] = plot_truncated
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
    try:
        resultlist = request.session['resultlist']
    except:
        raise Http404
    length = request.session['resultlength']
    plot = request.session['search']
    sortby = 'default'
    start = (id-1)*10 + 1
    if start>length:
        raise Http404  
    end = id*10
    if end>length:
        end=length
    resultlist = resultlist[start:end+1]
    pagenum = ceil(length/10)
    context = {'resultlist':resultlist, 'page':range(1,pagenum+1), 'plot':plot, 'current':id, 'sortby':sortby}
    if resultlist:
        return render(request, 'booklist.html', context)        


def SortByView(request, id, value):
    try:
        resultlist = request.session['resultlist']
        if value == 'newest':
            resultlist=sort(resultlist, sort_by='year', reverse=True)
        elif value == 'oldest':
            resultlist=sort(resultlist, sort_by='year', reverse=False)
        else:
            resultlist=sort(resultlist, sort_by=value, reverse=False)
    except:
        raise Http404
    length = request.session['resultlength']
    plot = request.session['search']
    start = (id-1)*10 + 1
    if start>length:
        raise Http404  
    end = id*10
    if end>length:
        end=length
    resultlist = resultlist[start:end+1]
    pagenum = ceil(length/10)
    context = {'resultlist':resultlist, 'page':range(1,pagenum+1), 'plot':plot, 'current':id, 'sortby':value}
    if resultlist:
        return render(request, 'booklist.html', context)   

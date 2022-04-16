from django.shortcuts import render, redirect
from .forms import AdvancedSearchForm, SimpleSearchForm
from .utils import standard_search, adv_search, filter, sort
from django.http import Http404  
from math import ceil
from django.urls import reverse
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
            try:
                # use standard search function 
                resultlist, length = standard_search(title=title, author=author, isbn=isbn, subject=genretuple)
                request.session['resultlength'] = length
                request.session['resultlist'] = resultlist
            except:
                request.session['resultlist'] = None
            # get search input to be displayed 
            if title:
                search = title+'...'
            elif isbn:
                search = isbn+'...'
            elif author:
                search = author+'...'
            elif genres:
                search = genres+'...'
            request.session['search'] = search
            resultlist = request.session['resultlist']
            if resultlist:
                return redirect(reverse('search:result', kwargs={'id': 1}))
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
            try:
                # use advanced search function 
                resultlist, length = adv_search(plot=plot)
                request.session['resultlength'] = length
                request.session['resultlist'] = resultlist
            except: 
                request.session['resultlist'] = None

            # get search input to be displayed 
            try:
                plot_truncated = plot[:30] + '...'
            except:
                plot_truncated=plot

            request.session['search'] = plot_truncated
            resultlist = request.session['resultlist']
            if resultlist:
                return redirect(reverse('search:result', kwargs={'id': 1}))
            else:
                messages.error(
                    request, f"Sorry, no matching books can be found!"
                )
    else: 
        form = AdvancedSearchForm()
    context = {'form': form}
    return render(request, 'advsearch.html', context)


def ResultView(request, id=id):
    # get results from session
    try:
        resultlist = request.session['resultlist']
    except:
        raise Http404
    # get length of results
    length = request.session['resultlength']
    plot = request.session['search']
    sortby = 'default'
    # get first book in page
    start = (id-1)*10 + 1
    if start>length:
        raise Http404  
    # get last book in page 
    end = id*10
    if end>length:
        end=length
    resultlist = resultlist[start:end+1]
    # get number of pages
    pagenum = ceil(length/10)
    context = {'resultlist':resultlist, 'page':range(1,pagenum+1), 'plot':plot, 'current':id, 'sortby':sortby}
    if resultlist:
        return render(request, 'booklist.html', context)        


def SortByView(request, id, value):
    # get results from session and use sort function 
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
    # get length of results
    length = request.session['resultlength']
    plot = request.session['search']
    # get first book in page
    start = (id-1)*10 + 1
    if start>length:
        raise Http404  
    # get last book in page 
    end = id*10
    if end>length:
        end=length
    resultlist = resultlist[start:end+1]
    # get number of pages
    pagenum = ceil(length/10)
    context = {'resultlist':resultlist, 'page':range(1,pagenum+1), 'plot':plot, 'current':id, 'sortby':value}
    if resultlist:
        return render(request, 'booklist.html', context)   

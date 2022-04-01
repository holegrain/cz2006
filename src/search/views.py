from django.shortcuts import render
from .utils import simple_search, adv_search, sort, filter

# Create your views here.
def SearchView(request):
    return render(request, 'search.html', {})


def AdvSearchView(request):
    return render(request, 'advsearch.html')
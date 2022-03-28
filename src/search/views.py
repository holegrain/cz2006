from django.shortcuts import render

# Create your views here.
def SearchView(request):
    return render(request, 'search.html', {})


def AdvSearchView(request):
    return render(request, 'advsearch.html')
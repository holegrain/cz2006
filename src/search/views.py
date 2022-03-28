from django.shortcuts import render

# Create your views here.
def SearchView(request):
    return render(request, 'search.html', {})
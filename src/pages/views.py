from django.shortcuts import render

# Create your views here.
# renders page not found template
def page404(request, exception):
    return render(request, "404.html", {})


# renders permission forbidden template
def page403(request, exception):
    return render(request, "403.html", {})


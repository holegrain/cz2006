from django.shortcuts import render, redirect
from .utils import Recommendation, ColdStart
from django.http import Http404  
from django.contrib import messages
from math import ceil
from star_ratings.models import UserRating
from django.contrib.auth.decorators import login_required

@login_required(login_url='/account/login/')
def recommend(request):
    if UserRating.objects.filter(user=request.user).exists():
        ratelist = UserRating.objects.filter(user=request.user)
        l = [rate for rate in ratelist]
        if len(l) < 5:
            msg = 'Please rate at least {N} more books to unlock recommendations!'
            messages.error(request, msg.format(5-len(l)))
        else:
            users = UserRating.objects.all()
            u = [user for user in users]
            if len(u)<10:
                recommendlist = ColdStart(request)
            else:
                recommendlist = Recommendation(request)
            return redirect('http://127.0.0.1:8000/search/1')
    else:
        messages.error(request, 'Please rate at least 5 more books to unlock recommendations!')

def ResultView(request, id=id):
    resultlist = request.session['resultlist']
    length = request.session['resultlength']
    start = (id-1)*10 + 1
    if start>length:
        raise Http404  
    end = id*10
    if end>length:
        end=length
    resultlist = resultlist[start:end]
    pagenum = ceil(length/10)
    context = {'resultlist':resultlist, 'page':range(1,pagenum+1), 'current':id}
    if resultlist:
         return render(request, 'booklist.html', context)
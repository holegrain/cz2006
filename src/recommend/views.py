from django.shortcuts import render, redirect
from .utils import Recommendation, ColdStart
from django.http import Http404  
from django.contrib import messages
from math import ceil
from books.models import Save
from star_ratings.models import UserRating
from accounts.models import User
from django.contrib.auth.decorators import login_required


@login_required(login_url='/account/login/')
def Recommend(request):
    if UserRating.objects.filter(user=request.user).exists():
        numrate = UserRating.objects.filter(user=request.user).count() # number of books the user has rated
        if numrate < 5:
<<<<<<< HEAD
            msg = 'Please rate at least {0} more books to unlock recommendations!'.format(5-numrate)
            messages.error(request, msg)
=======
            msg = 'Please rate at least {N} more books to unlock recommendations!'
            messages.error(request, msg.format(5-numrate))
            return redirect('/')
>>>>>>> c2c58b8b9c18a6c322c607252e549b0c427d92e0
        else:
            totalusers = User.objects.count() # total number of users
            totalratings = UserRating.objects.count() # total number of ratings
            if (totalusers<10 or totalratings<50): # less than 10 users or 50 ratings in total
                recommendlist, length = ColdStart(request)
            else:
                recommendlist, length = Recommendation(request)
                if length < 20: # coldstart if not enough recommendations
<<<<<<< HEAD
                    recommendlist1, length = ColdStart(request)
                    recommendlist = recommendlist.append(recommendlist1)[:100]
                    length = length(recommendlist)
=======
                    recommendlist1, length1 = ColdStart(request)
                    recommendlist = (recommendlist + recommendlist1)[:100]
                    length = len(recommendlist)
>>>>>>> c2c58b8b9c18a6c322c607252e549b0c427d92e0
            request.session['resultlength'] = length
            request.session['resultlist'] = recommendlist
            return redirect('http://127.0.0.1:8000/recommend/1')
    else:
        messages.error(request, 'Please rate at least 5 more books to unlock recommendations!')
        return redirect('/')

def ResultView1(request, id=id):
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
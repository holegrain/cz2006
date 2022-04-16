from django.shortcuts import render, redirect
from .utils import Recommendation, ColdStart
from django.http import Http404  
from django.contrib import messages
from math import ceil
from books.models import Save
from star_ratings.models import UserRating
from accounts.models import User
from django.urls import reverse
from django.contrib.auth.decorators import login_required


@login_required(login_url='/account/login/')
def Recommend(request):
    if UserRating.objects.filter(user=request.user).exists():
        numrate = UserRating.objects.filter(user=request.user).count() # number of books the user has rated
        if numrate < 5:
            msg = 'Please rate at least {0} more books to unlock recommendations!'.format(5-numrate)
            messages.error(request, msg)
            return redirect('/')
        else:
            totalusers = User.objects.count() # total number of users
            totalratings = UserRating.objects.count() # total number of ratings
            if (totalusers<10 or totalratings<50): # less than 10 users or 50 ratings in total
                recommendlist, length = ColdStart(request)
            else:
                recommendlist, length = Recommendation(request)
                if length < 20: # coldstart if not enough recommendations
                    recommendlist1, length1 = ColdStart(request)
                    recommendlist = recommendlist + recommendlist1
                    length += length1
                try:
                    if length<=100:
                        pass
                    else:   
                        recommendlist = recommendlist[:100]
                        length = length(recommendlist)
                except:
                    messages.error(
                        request, f'No Recommendations found!'
                    )
            request.session['resultlength'] = length
            request.session['resultlist'] = recommendlist
            return redirect(reverse('recommend:result1', kwargs={'id': 1}))
    else:
        messages.error(request, 'Please rate at least 5 more books to unlock recommendations!')
        return redirect('/')


def ResultView1(request, id=id):
    # get results from session
    try:
        resultlist = request.session['resultlist']
    except:
        raise Http404
    # get length of results
    length = request.session['resultlength']
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
    context = {'resultlist':resultlist, 'page':range(1,pagenum+1), 'current':id}
    if resultlist:
         return render(request, 'reclist.html', context)
from django.shortcuts import render, HttpResponse, redirect
from nlbsg import Client
from nlbsg.catalogue import PRODUCTION_URL
from nlbsg import MediaCode
import mysql.connector
from books.models import Save
from star_ratings.models import UserRating
from django.contrib.auth.models import User
from itertools import combinations
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

'''
For more information, visit:
https://medium.com/web-mining-is688-spring-2021/collaborative-book-recommendation-system-24a5aba2d2ed
https://realpython.com/build-recommendation-engine-collaborative-filtering/ 
https://towardsdatascience.com/building-and-testing-recommender-systems-with-surprise-step-by-step-d4ba702ef80b
'''

API_KEY = 'RGV2LVpob3VXZWk6IW5sYkAxMjMj'

client = Client(PRODUCTION_URL, API_KEY)

db = mysql.connector.connect(host='114.119.173.226', database='library', user='root', 
                             password='Cheesec@ke')
cursor = db.cursor()

def Recommendation(request):
    users = UserRating.objects.values_list('user', flat=True)
    bids = list(UserRating.objects.values_list('rating', flat=True))
    ratings = list(UserRating.objects.values_list('score', flat=True))
    userids = []
    for user in users:
        userids.append(user.id)
    df = pd.DataFrame(list(zip(userids, bids, ratings)), columns=['UserID', 'BID', 'Rating'])
    # Futher filtering of df could be done e.g. remove books with less than N total ratings or books/user with less than X ratings.
    # KNN Collaborative Filtering
    df_pivot = df.pivot(index='BID', columns='UserID', values='Rating').fillna(0)
    df_matrix = csr_matrix(df_pivot.values)
    model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
    model_knn.fit(df_matrix)

    ratelist = UserRating.objects.filter(user=request.user)
    recolist = []
    bidset = set()
    for rate in ratelist:
        bidset.add(rate.rating.bid)
        if rate.score > 2:
            recolist.append(rate.rating.bid)

    resultbid = set()
    for bid in recolist:
        index = df_pivot.index.get_loc(bid)
        distances,indices=model_knn.kneighbors(df_pivot.iloc[index,:].values.reshape(1,-1),n_neighbors=6)
        for i in range(0, len(distances.flatten())):
            if distances.flatten()[i] > 0.5:
                pass
            else:
                resultbid.add(df_pivot.index[indices.flatten()[i]])
        if len(resultbid-bidset) > 20:
            break  
    result = list(resultbid-bidset)
    if len(result) > 20:
        result = result[:20]
    return result

def ColdStart(request):
    ratelist = UserRating.objects.filter(user=request.user)
    if Save.objects.filter(user=request.user).exists():
        savelist = Save.objects.filter(user=request.user)
    bidlist = []
    for rate in ratelist:
        bidlist.append(rate.rating.bid)
    for save in savelist:
        bidlist.append(save.bid)
    bidset = set(bidlist)
    subjectdict = {}
    for bid in bidlist:
        details = client.get_title_details(bid=bid)
        if details.status=='FAIL':
            pass
        else:
            subjecttuple = details.title_detail.subjects
            for subject in subjecttuple:
                count = subjectdict.get(subject)
                if count is None:
                    subjectdict[subject] = 1
                else:
                    subjectdict[subject] += 1

    topsubjects = []
    if len(subjectdict) > 10:
        for x in range(10):
            topsubjects.append(max(subjectdict, key=subjectdict.get))
            subjectdict.pop(topsubjects[x])
    else: # less than 10 subjects from books rated/saved by the user
        for x in subjectdict.keys():
            topsubjects.append(x)

    num = len(topsubjects)
    resultbid = set()
    if num > 3:
        count = 3
    else:
        count = num
    while len(resultbid-bidset) < 20 and count > 0:
        combs = combinations(topsubjects, count)
        for comb in combs:  
            if len(resultbid-bidset) > 20:
                break  
            responses = client.search(subject=comb, media_code=MediaCode.BOOKS, limit=100)
            if responses.titles is None:
                continue
            else: 
                for response in responses.titles:
                    resultbid.add(response.bid)
        count -= 1
    result = list(resultbid-bidset)
    if len(result) > 20:
        result = result[:20]
    return result

'''# test
ratelist = UserRating.objects.all()
bidlist = []
for rate in ratelist:
    bidlist.append(rate.rating.bid)
bidset = set(bidlist)
print(bidset)'''
from nlbsg import Client
from nlbsg.catalogue import PRODUCTION_URL
from nlbsg import MediaCode
import mysql.connector
from itertools import combinations
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from books.models import Book, Save
from star_ratings.models import UserRating

'''
For more information, visit:
https://medium.com/web-mining-is688-spring-2021/collaborative-book-recommendation-system-24a5aba2d2ed
https://realpython.com/build-recommendation-engine-collaborative-filtering/ 
https://towardsdatascience.com/building-and-testing-recommender-systems-with-surprise-step-by-step-d4ba702ef80b
'''

API_KEY = 'RGV2LVpob3VXZWk6IW5sYkAxMjMj'
client = Client(PRODUCTION_URL, API_KEY) # initialise the nlb client

# initialise mysql connection
db = mysql.connector.connect(host='114.119.173.226', database='library', user='root', 
                             password='Cheesec@ke')
cursor = db.cursor()

def Recommendation(request):
    userids = list(UserRating.objects.values_list('user', flat=True)) # list of userids
    ratings = list(UserRating.objects.values_list('score', flat=True)) # list of ratings
    bids = [] # list of bids
    for userrating in UserRating.objects.all():
        bids.append(userrating.rating.content_object.bid)
    df = pd.DataFrame(list(zip(userids, bids, ratings)), columns=['UserID', 'BID', 'Rating']) 
    # Futher filtering of df could be done e.g. remove books with less than N total ratings or books/user with less than X ratings.
    # KNN Collaborative Filtering
    df_table = df.pivot_table(index='BID', columns='UserID', values='Rating').fillna(0) # fill empty ratings with 0
    #df_pivot = df.pivot(index='BID', columns='UserID', values='Rating').fillna(0) 
    
    df_matrix = csr_matrix(df_table)
    model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
    model_knn.fit(df_matrix)

    userratings = UserRating.objects.filter(user=request.user) # queryset of UserRating objs
    recolist = [] # list of books to generate recommendations
    bidset = set() # set of bids rated by user
    for userrating in userratings:
        bidset.add(userrating.rating.content_object.bid) 
        if userrating.score > 2: # find similar books for books with rating more than 2
            recolist.append(userrating.rating.content_object.bid)

    resultbid = set() # recommended set of bids
    for bid in recolist:
        index = df_table.index.get_loc(bid)
        distances,indices=model_knn.kneighbors(df_table.iloc[index,:].values.reshape(1,-1),n_neighbors=10)
        for i in range(0, len(distances.flatten())):
            if distances.flatten()[i] > 0.5: 
                pass
            else:
                resultbid.add(df_table.index[indices.flatten()[i]])
        if len(resultbid-bidset) > 100:
            break  

    results = list(resultbid-bidset) # recommended list of bids
    if len(results) > 100:
        results = results[:100]
    resultlist = []
    for result in results:
        title_details = client.get_title_details(bid=result) # get the details of each book
        if title_details.title_detail is not None:
            isbn = title_details.title_detail.isbn.split()[0] if title_details.title_detail.isbn is not None else None
            name = title_details.title_detail.title_name
            author = title_details.title_detail.author
            plot = title_details.title_detail.summary
            #year = Book.objects.get(bid=result).year
            bid = title_details.title_detail.bid
            if name is not None and plot is not None:
                plot = plot.replace('&#8212', '-')
                resultlist.append({'isbn': isbn, 'title': name, 'plot': plot, 'year': None,
                                'author': author, 'bid': bid}) # get only the important information
    return resultlist, len(resultlist)

def ColdStart(request):
    userratings = UserRating.objects.filter(user=request.user) # queryset of UserRating objs 
    savelist = []
    if Save.objects.filter(user=request.user).exists():
        savelist = Save.objects.filter(user=request.user)
    bidset = set() # set of bids saved/rated by the user
    recoset = set() # set of bids to generate recommendations
    for userrating in userratings:
        bidset.add(userrating.rating.content_object.bid) 
        if userrating.score > 2: # find similar books for books with rating more than 2
            recoset.add(userrating.rating.content_object.bid)
    for save in savelist:
        bidset.add(save.bid)
        recoset.add(save.bid)

    subjectdict = {} # dict to count subject occurrences 
    for bid in recoset:
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

    topsubjects = [] # list of most popular subjects 
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
    while len(resultbid-bidset) < 100 and count > 0:
        combs = combinations(topsubjects, count)
        for comb in combs:  
            if len(resultbid-bidset) > 100:
                break  
            responses = client.search(subject=comb, media_code=MediaCode.BOOKS, limit=25)
            #titles = list(responses.titles) # titles is a list of Title objects
            if responses.titles is None:
                continue
            else: 
                for response in responses.titles:
                    resultbid.add(response.bid)
        count -= 1

    results = list(resultbid-bidset)
    if len(results) > 100:
        results = results[:100]
    resultlist = []
    for result in results:
        title_details = client.get_title_details(bid=result) # get the details of each book
        if title_details.title_detail is not None:
            isbn = title_details.title_detail.isbn.split()[0] if title_details.title_detail.isbn is not None else None
            name = title_details.title_detail.title_name
            author = title_details.title_detail.author
            plot = title_details.title_detail.summary
            #year = Book.objects.get(bid=result).year
            bid = title_details.title_detail.bid
            if name is not None and plot is not None:
                plot = plot.replace('&#8212', '-')
                resultlist.append({'isbn': isbn, 'title': name, 'plot': plot, 'year': None,
                                'author': author, 'bid': bid}) # get only the important information
    return resultlist, len(resultlist)
import yake
import nlbsg
import numpy as np
import mysql.connector
from itertools import combinations
from typing import Optional, Union
from typing_extensions import Literal
from nlbsg.catalogue import PRODUCTION_URL
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from nlbsg import MediaCode

API_KEY = 'RGV2LVpob3VXZWk6IW5sYkAxMjMj'

model = SentenceTransformer('bert-base-nli-mean-tokens')
client = nlbsg.Client(PRODUCTION_URL, API_KEY) # initialise the nlb client

# zhouw: simple_search replaced with standard_search. client.search cannot search using isbn or bid. If have questions text in grp.
# zhouw: Added bid to simple/standard search options. Yall okay with this?
search_options = ['title', 'isbn', 'bid', 'author', 'genre']
#search_options = ['title', 'isbn', 'author', 'genre']

# initialise mysql connection
db = mysql.connector.connect(host='114.119.173.226', database='library', user='root', 
                             password='Cheesec@ke')
cursor = db.cursor()

def standard_search(**kwargs) -> Optional[list]:
    bidset = set()
    resultlist = []
    if kwargs['isbn']:
        item = client.get_title_details(isbn=kwargs['isbn'])
        if item.status!='FAIL':
            bidset.add(item.title_detail.bid)

    if kwargs['bid']:
        item = client.get_title_details(isbn=kwargs['bid'])
        if item.status!='FAIL':
            bidset.add(item.title_detail.bid)

    searchresult = client.search(title=kwargs['title'], author=kwargs['author'], subject=kwargs['genre'], media_code=MediaCode.BOOKS, limit=20)
    if searchresult.titles is None:
        pass
    else:
        for title in searchresult.titles: 
            bidset.add(title.bid)

    for bid in bidset:
        book = client.get_title_details(bid=bid)
        #moreinfo = client.search(title=book.title_detail.title_name, media_code=MediaCode.BOOKS, limit=1)
        result = {'isbn': book.title_detail.isbn, 'bid': book.title_detail.bid, 
                'title': book.title_detail.title_name, 'plot': book.title_detail.summary, 'author': book.title_detail.author}
                #'year': year}
        resultlist.append(result)
    return resultlist
        
# zhouwe: client.search does not search using isbn nor bid.
'''def simple_search(**kwargs) -> Optional[list]:
    for item in list(kwargs.keys()):
        if item not in search_options or kwargs[item] is None: # filter out irrelevant arguments
            kwargs.pop(item)
    
    # zhouw: Can remove because SimpleSearchForm took care of this.
    if len(kwargs) == 0: # no input
        return None

    responses = client.search(**kwargs, limit=50)
    titles = list(responses.titles) # titles is a list of Title objects

    # obtain the plot of each book
    plots = [client.get_title_details(item.bid).title_detail.summary for item in titles]

    # return same thing as advanced search
    return [{'isbn': item.isbn, 'bid': item.bid, 'title': item.title_name, 'plot': plot, 'year': item.publish_year, 
             'author': item.author} for item, plot in zip(titles, plots)]
'''

def adv_search(plot: Optional[str] = None, keywords: Union[str, list] = None) -> Optional[list]:
    if plot is None and keywords is None: # check input validity
        return None

    # to reduce the search space, first filter by keywords
    if keywords is None: # extract keywords from plot
        kw_extractor = yake.KeywordExtractor(top=10, stopwords=None)
        keywords = kw_extractor.extract_keywords(plot)
        # sort the keywords by confidence score
        keywords = [k for k, _ in sorted(keywords, key=lambda x: x[1], reverse=True)][:5]
        
    total_books = []
    
    keyword_length = max(len(keywords), 5) # get maximum number of word choices

    for i in range(keyword_length, 0, -1): # reduce the number of keywords searched in a loop
        books = kw_search(keywords, i, client) 

        if books: # if not empty list
            total_books.extend([i for i in books if i not in total_books])
            
            if len(total_books) >= 70: # enough candidates
                break

        elif len(total_books)==0 and i==1: # no books at all at the end of loop
            return None

    rec_cand = []

    for book in total_books:
        bid = book.bid
        isbn = book.isbn.split()[0]
        title_details = client.get_title_details(bid) # get the details of each book
        if title_details.title_detail is not None:
            name = title_details.title_detail.title_name
            author = title_details.title_detail.author
            plot = title_details.title_detail.summary
            year = book.publish_year if book.publish_year is not None else '0000'
            # author = title_details.title_detail.author
            if name is not None and plot is not None:
                plot = plot.replace('&#8212', '-')
                rec_cand.append({'isbn': isbn, 'title': name, 'plot': plot, 'year': year,
                                 'author': author}) # get only the important information
    
    sentences = [i['plot'] for i in rec_cand]
    sentence_emb = model.encode([plot]+sentences) # embed the sentences
    sim = cosine_similarity([sentence_emb[0]], sentence_emb[1:])[0] # find similarity
    sorted_sim_idx = np.argsort(sim)[::-1] # from most similar to least similar
    ranked_candidates = [rec_cand[i] for i in sorted_sim_idx] # rank the candidates

    return ranked_candidates[:10]


def kw_search(keywords: list, count: int, client: nlbsg.Client) -> nlbsg.types.SearchResponse:
    combs = combinations(keywords, count) # get all combination of i words from n words
    r_list = []

    for comb in combs:

        responses = client.search(keywords=comb, media_code=nlbsg.MediaCode.BOOKS, limit=100)

        if responses.total_records != 0:
            r_list.extend([i for i in responses.titles]) # only collect the item in response.titles

    return r_list


def filter(results: list, year: int) -> list:
    # assume result is a list of [(bookname, plot, year)]
    return [i for i in results if int(i['year']) >= year]


def sort(results: list, sort_by: Literal['title', 'author', 'year', 'popularity'], reverse: Literal[True, False]) \
        -> Optional[list]:
    # if sort by title, author or year is easy
    if sort_by in ['title', 'author', 'year']:
        return sorted(results, key=lambda x: x[sort_by], reverse=reverse)
    
    elif sort_by == 'popularity':
        popularity = []
        # else do sql query
        isbns = [result['isbn'] for result in results]
        for isbn in isbns:
            query = f"SELECT * FROM views WHERE isbn = {isbn}"
            cursor.execute(query)

            count = len(cursor.fetchall()) # get number of views
            popularity.append((isbn, count))
    
        sorted_results = [r for r, _ in sorted(zip(results, popularity), \
                          key=lambda x: x[1][1], reverse=True)] # sort by the count

        return sorted_results
    
    return None


'''if __name__ == "__main__":
    # define a test result list
    books = [{'isbn': '1', 'title': 'a', 'author':'c', 'plot': 'z', 'year': '2000'}, 
             {'isbn': '2', 'title': 'b', 'author':'b', 'plot': 'y', 'year': '2001'},
             {'isbn': '3', 'title': 'c', 'author':'a', 'plot': 'x', 'year': '2002'}]
    print(sort(books, sort_by='title', reverse=True))
    print(sort(books, sort_by='author', reverse=False))
    print(sort(books, sort_by='year', reverse=True))
    print(filter(books, year=2001))
    print(simple_search(title='sherlock', kek='abc', author=None)) # check function
    test_str = "he is a detective, big dog"
    print(adv_search(test_str))'''

'''ls = standard_search(title='Jane Eyre')
for x in ls.titles:
    print(x.title_name)'''
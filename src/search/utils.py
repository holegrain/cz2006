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

search_options = ['title', 'isbn', 'author', 'subject']

# initialise mysql connection
db = mysql.connector.connect(host='114.119.173.226', database='library', user='root', 
                             password='Cheesec@ke')
cursor = db.cursor()

def standard_search(**kwargs) -> Optional[list]:
    if kwargs['isbn'] != '':
        item = client.get_title_details(isbn=kwargs['isbn'])
        if item.status!='FAIL':
            item = item.title_detail
            return [{'isbn': item.isbn, 'bid': item.bid, 'title': item.title_name, 'plot': item.summary, \
                     'year': 'Unknown', 'author': item.author}]

        else:
            return None
# search gives {'title': 'Jane eyre', 'author': '', 'isbn': '', 'bid': None, 'subject': ('',)}
    else:
        for k in list(kwargs.keys()):
            if k == 'subject' and kwargs[k] == ('',):
                kwargs.pop(k)
            else:
                if kwargs[k] == '':
                    kwargs.pop(k)
        
        if len(kwargs) == 0:
            return None

        responses = client.search(**kwargs, limit=100)
        if responses.titles is not None:
            titles = list(responses.titles) # titles is a list of Title objects
        else:
            return None
        
        plots = []
        # obtain the plot of each book
        for item in titles:
            if client.get_title_details(item.bid).title_detail is not None:
                plots.append(client.get_title_details(item.bid).title_detail.summary)
            else:
                plots.append('None')
        # return same thing as advanced search
        return [{'isbn': item.isbn, 'bid': item.bid, 'title': item.title_name, 'plot': plot, \
                 'year': item.publish_year, 'author': item.author} for item, plot in zip(titles, plots)], len(titles)
        

def adv_search(plot: Optional[str] = None, keywords: Union[str, list] = None) -> Optional[list]:
    
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
        if book.isbn != None:
            isbn = book.isbn.split()[0]
        else: 
            isbn = None
        title_details = client.get_title_details(bid) # get the details of each book
        if title_details.title_detail is not None:
            name = title_details.title_detail.title_name
            author = title_details.title_detail.author
            plot = title_details.title_detail.summary
            year = book.publish_year if book.publish_year is not None else '0000'
            bid = title_details.title_detail.bid
            if name is not None and plot is not None:
                plot = plot.replace('&#8212', '-')
                rec_cand.append({'isbn': isbn, 'title': name, 'plot': plot, 'year': year,
                                 'author': author, 'bid': bid}) # get only the important information

    sentences = [i['plot'] for i in rec_cand]
    sentence_emb = model.encode([plot]+sentences) # embed the sentences
    sim = cosine_similarity([sentence_emb[0]], sentence_emb[1:])[0] # find similarity
    sorted_sim_idx = np.argsort(sim)[::-1] # from most similar to least similar
    ranked_candidates = [rec_cand[i] for i in sorted_sim_idx] # rank the candidates
    if len(ranked_candidates)>100:
        return ranked_candidates[:100], 100
    else: 
        return ranked_candidates, len(ranked_candidates)


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


def sort(results: list, sort_by: Literal['title', 'year', 'popularity'], reverse: Literal[True, False]) \
        -> Optional[list]:
    # if sort by title, author or year is easy
    if sort_by in ['title', 'author', 'year']:
        return sorted(results, key=lambda x: x[sort_by], reverse=reverse)
    
    elif sort_by == 'popularity':
        popularity = []
        # else do sql query
        bids = [result['bid'] for result in results]
        for bid in bids:
            query = f"SELECT * FROM books_view WHERE bid = {bid}"
            cursor.execute(query)

            count = len(cursor.fetchall()) # get number of views
            popularity.append((bid, count))
    
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
import yake
import numpy as np
from itertools import combinations
from typing import Optional, Union
import nlbsg
from nlbsg.catalogue import PRODUCTION_URL
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

API_KEY = 'RGV2LVpob3VXZWk6IW5sYkAxMjMj'

model = SentenceTransformer('bert-base-nli-mean-tokens')
client = nlbsg.Client(PRODUCTION_URL, API_KEY) # initialise the nlb client

def adv_search(plot: Optional[str] = None, keywords: Union[str, list] = None) -> Union[list, str]:
    if plot is None and keywords is None: # check input validity
        return "Please provide some details for us to do the search for you!"

    # to reduce the search space, first filter by keywords
    if keywords is None: # extract keywords from plot
        kw_extractor = yake.KeywordExtractor(top=10, stopwords=None)
        keywords = kw_extractor.extract_keywords(plot)
        # sort the keywords by confidence score
        keywords = [k for k, _ in sorted(keywords, key=lambda x: x[1], reverse=True)][:5]
        
    total_responses = []
    
    keyword_length = max(len(keywords), 5) # get maximum number of word choices

    for i in range(keyword_length, 0, -1): # reduce the number of keywords searched in a loop
        responses = kw_search(keywords, i, client) 

        if responses is not None:
            total_responses.append(responses)
            if len(total_responses) >= 70: # enough candidates
                break

        elif responses is None and i==1:
            return "We were unable to find suitable books for you. \
                    We are very sorry and are working hard to improve \
                    the system to serve you better."


    rec_cand = []
    bids = set([book.bid for responses in total_responses for book in responses.titles])

    for bid in bids:
        title_details = client.get_title_details(bid) # get the details of each book
        if title_details.title_detail is not None:
            name = title_details.title_detail.title_name
            plot = title_details.title_detail.summary
            # author = title_details.title_detail.author
            if name is not None and plot is not None:
                plot = plot.replace('&#8212', '-')
                rec_cand.append((name, plot)) # get only the important information
    
    sentences = [i[1] for i in rec_cand]
    sentence_emb = model.encode([plot]+sentences) # embed the sentences
    sim = cosine_similarity([sentence_emb[0]], sentence_emb[1:])[0] # find similarity
    sorted_sim_idx = np.argsort(sim)[::-1] # from most similar to least similar
    ranked_candidates = [rec_cand[i] for i in sorted_sim_idx] # rank the candidates

    return ranked_candidates[:10]


def kw_search(keywords: list, count: int, client: nlbsg.Client) -> Union[nlbsg.types.SearchResponse, None]:
    combs = combinations(keywords, count) # get all combination of i words from n words

    for comb in combs:
        responses = client.search(keywords=comb, media_code=nlbsg.MediaCode.BOOKS, limit=100)

        if responses.total_records != 0:
            return responses

    return None

story = 'he is a detective, big dog'
print(*adv_search(plot=story), sep='\n')
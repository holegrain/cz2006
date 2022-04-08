'''
For more information please see:
https://nlbsg.readthedocs.io/en/latest/ 
'''

from nlbsg import Client
from nlbsg.catalogue import STAGING_URL, PRODUCTION_URL
from nlbsg import MediaCode

API_KEY = 'RGV2LVpob3VXZWk6IW5sYkAxMjMj'

client = Client(PRODUCTION_URL, API_KEY)

'''
search(keywords=None, author=None, subject=None, title=None, branch=None, media_code=None, 
language=None, sort=None, start=1, limit=10, set_id=None)
Searches content according to search criteria.

Parameters
-keywords (Optional[str])
-author (Optional[str]) 
-subject (Optional[str]) 
-title (Optional[str])
-branch (Union[str, Branch, None]) 
Include only results from a particular branch. See constants.Branch for possible values.

-media_code (Union[str, MediaCode, None])
Include only results of a particular media type. See constants.MediaCode for possible values.

-language (Union[str, Language, None]) 
Include only results in a particular language. See constants.Language for possible values.

-sort (Union[str, Sort, None]) 
By default, results are sorted by published year in descending order. 
Use PUBDATE to sort in ascending order instead, or TITLE to sort by title in ascending order, 
ignoring articles like “a”, “an” or “the”. These values can also be found in constants.Sort.

-start (int)
Start pointer for returned records.

-limit (int)
Maximum records to be returned. 
This is capped at 100 records even if a number greater than 100 is specified.

-set_id (Optional[str]) 
For use in pagination. This can be used with start to return the index position of the next record in the backend system.
'''
# Searching the catalogue
# To note: List of books returned is always the same for the same set of given inputs.
'''
Issues with search: 
Unable to have multiple keywords. 
Unable to have multiple subjects.
Possible solutions:

'''
results = client.search(title='', subject='Mystery', media_code=MediaCode.BOOKS, limit=5)
if results.titles is None:
    print('No matching books found. Please try again.')
else:
    for title in results.titles:
        print(f'Title: {title.title_name}\nISBN: {title.isbn}\nPublished: {title.publish_year}\n')

'''
get_title_details(bid=None, isbn=None)
Get detailed information about an item. Either bid or isbn should be provided.

Parameters
-bid (Optional[str])
-isbn (Optional[str])
'''
# Getting title details
# DO NOT USE RAW ISBN STRING e.g. '9781481468367 (electronic bk)' TO SEARCH 
# Strictly ISBN-10 or ISBN-13
details = client.get_title_details(isbn='9781338299175')
if details.status=='FAIL':
    print('No matching books found. Please try again.')
else:
    print(f'BID: {details.title_detail.bid}\nISBN: {details.title_detail.isbn}\n')
    print(f'Title: {details.title_detail.title_name}\nAuthor: {details.title_detail.author}\n')
    print(f'Subjects: {details.title_detail.subjects}\nSummary: {details.title_detail.summary}\n')
    
'''
get_availability_info(bid=None, isbn=None, sort=None, start=1, limit=10, set_id=None)
Check whether an item is available for loan. Either bid or isbn should be provided.

Parameters
-bid (Optional[str])
-isbn (Optional[str])
-sort (Union[str, Sort, None]) 
-start (int)
-limit (int) 
-set_id (Optional[str]) 
'''
# Getting title availability
'''availability = client.get_availability_info(isbn='1328915336')
for item in availability.items:
    print(f'Branch: {item.branch_name}\nStatus: {item.status_desc}\n')'''
import datetime
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .models import Book, Save, View
from nlbsg import Client
from nlbsg.catalogue import PRODUCTION_URL
from django.db.models import Q
'''
Keyword argument queries in filter(), etc. are “AND”ed together. 
If you need to execute more complex queries (for example, queries with OR statements), you can use Q objects.
A Q object (django.db.models.Q) is an object used to encapsulate a collection of keyword arguments. 
These keyword arguments are specified as in “Field lookups” above.

For more information, visit:
https://docs.djangoproject.com/en/4.0/topics/db/queries/ 
'''


# Create your views here.

API_KEY = 'RGV2LVpob3VXZWk6IW5sYkAxMjMj'
client = Client(PRODUCTION_URL, API_KEY)

# ViewBook() displays detailed book information and updates view history if user is logged in.
def ViewBook(request, bid):
    book = client.get_title_details(bid=bid)
    bookdetail = book.title_detail
    isSaved = False
    detail={
            'Title': bookdetail.title_name,
            'ISBN': bookdetail.isbn,
            'BID': bookdetail.bid,
            'Author': bookdetail.author,
            'Other_authors': bookdetail.other_authors,
            'Publisher': bookdetail.publisher,
            'Physical_desc': bookdetail.physical_desc,
            'Subjects': bookdetail.subjects,
            'Summary': bookdetail.summary,
            'Notes': bookdetail.notes,
            'Saved': isSaved,
            'URL': "domainname.com/books/"+bookdetail.bid
        }
    
    if Book.objects.filter(bid=bid).exists():
            RatedBook = Book.objects.get(bid=bid)
    else:
        RatedBook = Book(bid=bid)
        RatedBook.save()
    if request.session.has_key('is_logged'):
        if Save.objects.filter(Q(user=request.user), Q(bid=bid)).exists():
            isSaved = True
            detail['Saved'] = isSaved
        if View.objects.filter(Q(user=request.user), Q(bid=bid)).exists():
            # Book has been viewed before by the user.
            ViewedBook = View.objects.get(user=request.user, bid=bid)
            ViewedBook.lastviewed = datetime.datetime.now()
            ViewedBook.save()
        else:
            # Book is not among the last 20 books viewed by the user.
            ViewedBook = View(user=request.user, bid=bid, lastviewed=datetime.datetime.now())
            ViewedBook.save()
        try:
            userview = View.objects.filter(user=request.user)
            top20 = View.objects.filter(user=request.user).order_by('-lastviewed')[:20]
            for i in userview:
                if i not in top20:
                    i.delete()
        except:
            pass
        if request.method == 'POST':
            heartclicked = request.POST['clicked']
            book = Save.objects.filter(Q(user=request.user), Q(bid=bid)).first()
            if book:
                book.delete()
                return render(request,'book.html', {'detail': detail, 'RatedBook': RatedBook})
            else:
                book = Save(user=request.user, bid=bid)
                book.save()
                return render(request,'booksaved.html', {'detail': detail, 'RatedBook': RatedBook})
    if isSaved:
        return render(request,'booksaved.html', {'detail': detail, 'RatedBook': RatedBook})
    else: 
        return render(request,'book.html', {'detail': detail, 'RatedBook': RatedBook})
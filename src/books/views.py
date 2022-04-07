import datetime
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .models import Rate, Save, View
from nlbsg import Client
from nlbsg.catalogue import PRODUCTION_URL
from .forms import RatingForm
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
            'Rating': 0,
            'Saved': isSaved,
            'URL': "domainname.com/books/"+bookdetail.bid
        }
    if request.session.has_key('is_logged'):
        if Rate.objects.filter(Q(user=request.user), Q(bid=bid)).exists():
            RatedBook = Rate.objects.get(Q(user=request.user), Q(bid=bid))
            detail['Rating'] = RatedBook.rating
        if Save.objects.filter(Q(user=request.user), Q(bid=bid)).exists():
            isSaved = True
            detail['Saved'] = isSaved
        if View.objects.filter(Q(user=request.user), Q(bid=bid)).exists():
            # Book has been viewed before by the user.
            ViewedBook = View.objects.get(user=request.user, bid=bid)
            ViewedBook.lastviewed = datetime.datetime.now()
            ViewedBook.save()
            try:
                top20 = View.objects.filter(user=request.user).order_by('-lastviewed')[:20]
                View.objects.exclude(bid=top20.bid).delete()
            except:
                pass
        else:
            # Book is not among the last 20 books viewed by the user.
            ViewedBook = View(user=request.user, bid=bid, lastviewed=datetime.datetime.now())
            ViewedBook.save()
    if request.method == 'POST':
        heartclicked = request.POST['clicked']
        book = Save.objects.filter(Q(user=request.user), Q(bid=bid)).first()
        if book:
            book.delete()
            return render(request,'book.html', detail)
        else:
            book = Save(user=request.user, bid=bid)
            book.save()
            return render(request,'booksaved.html', detail)
    if isSaved:
        return render(request,'booksaved.html', detail)
    else: 
        return render(request,'book.html', detail)
        
# RateBook() 
def RateBook(request, bid):
    if request.session.has_key('is_logged'):
        if request.method == 'POST':
            form = RatingForm(request.POST)
            if form.is_valid():
                rating = form.clean_data.get('rating') 
                if Rate.objects.filter(Q(user=request.user), Q(bid=bid)).exists():
                    RatedBook = Rate.objects.get(Q(user=request.user), Q(bid=bid))
                    RatedBook.rating = rating
                else:
                    RatedBook = Rate(user=request.user, bid=bid, rating=rating)
                RatedBook.save()
                messages.success(request, f'Your account successfully updated.')
        else:
            form = RatingForm()
    else:
        messages.error(request, f"Please login to rate books!")
    context = {'form': form, 'object': RatedBook}
    return render(request, 'profile.html', context)


# SaveBook() handles the backend of saving/unsaving books.            
def SaveBook(request, bid):
    if request.session.has_key('is_logged'):
        if request.method == 'POST':
            if Save.objects.filter(Q(user=request.user), Q(bid=bid)).exists():
                SavedBook = Save.objects.get(Q(user=request.user), Q(bid=bid))
                SavedBook.delete()
                messages.success(request, 'Unsaved!')
            else:
                SavedBook = Save(user=request.user, bid=bid)
                SavedBook.save()
                messages.success(request, 'Saved!')
        else:
            return 
    else:
        messages.error(request, 'Please login to rate books!')

# ShareBook()
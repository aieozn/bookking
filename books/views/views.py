from django.shortcuts import render
from django.shortcuts import redirect

from books.forms import BookForm, BookCreator
from books.models import Author, Category, Book
from books.views.paginator import Paginator


def index(request, id=0):
    """ Home page view

    Args:
        id (int, optional): Unused variable for url convention.
        Defaults to 0.
    """

    categories = Category.objects.all().order_by('name')
    authors = Author.objects.all().order_by('name')

    context = {
        'categories': categories,
        'authors': authors,
        'title': 'BookKing'
    }
    return render(request, 'books/home.html', context)


def new_book(request):
    """ New book form view and POST validator """

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)

        if form.is_valid():
            BookCreator().save(form.data, request)
            return redirect('/new/')
        else:
            print(form.errors)

    categories = Category.objects.all().order_by('name')
    authors = Author.objects.all().order_by('name')
    context = {
        'form': BookForm(),
        'categories': categories,
        'authors': authors,
    }
    return render(request, 'books/newBook.html', context)


def page(request, pagenum):
    """ Asynchronously loaded list of books """
    context = Paginator().filter(Book.objects.all(), pagenum)
    return render(request, 'books/bookListPage.html', context)


def category_filtered(request, category_id, pagenum):
    context = Paginator().filter(
        Book.objects.filter(categories__pk=category_id),
        pagenum
    )
    return render(request, 'books/bookListPage.html', context)


def author_filtered(request, author_id, pagenum):
    context = Paginator().filter(
        Book.objects.filter(authors__pk=author_id),
        pagenum
    )
    return render(request, 'books/bookListPage.html', context)


def request_filtered(request, request_id, pagenum):
    context = Paginator().filter(
        Book.objects.filter(request__pk=request_id),
        pagenum
    )
    return render(request, 'books/bookListPage.html', context)


def search(request):
    """ Search view """
    categories = Category.objects.all().order_by('name')
    authors = Author.objects.all().order_by('name')

    context = {
        'categories': categories,
        'authors': authors,
    }
    return render(request, 'books/search.html', context)

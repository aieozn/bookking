import threading

from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from books.models import Request, Category, Book, Author
from books.usecases.apiadapter import BookReader


@require_http_methods(["POST"])
def search_init(request):
    """
    Creates new Request object.
    Returns its id to allow the frontent layer to track changes
    """
    keywords = request.POST.get('keywords', None)

    total = 0
    key = -1
    error = True

    if keywords:
        # search for a full phrase
        keywords = "\"" + keywords + "\""

        new_request = Request()
        new_request.create(keywords)
        key = new_request.pk
        total = new_request.total

        book_reader = BookReader()

        if total > 0:
            collector = threading.Thread(
                target=book_reader.process_request,
                args=(new_request,)
            )

            collector.start()

        error = new_request.error

    request_status = {
        'id': key,
        'total': total,
        'error': error,
    }

    return JsonResponse(request_status)


@require_http_methods(["POST"])
def clear(request):
    """ Removes all books informations from database """
    Request.objects.all().delete()
    Category.objects.all().delete()
    Author.objects.all().delete()
    Book.objects.all().delete()

    # From post to get through redirect :)
    return redirect('/')


def search_status(request, id):
    """ Asynchronously called function,
    returns request progress

    Args:
        id (Int): Request primary key

    Returns:
        JSON: Acctual request status and progress
    """

    try:
        acct_request = Request.objects.get(pk=id)
    except Request.DoesNotExist:
        return JsonResponse({})

    response = {
        'status': acct_request.finished,
        'found': acct_request.found,
        'total': acct_request.total,
        'error': acct_request.error,
    }

    return JsonResponse(response)

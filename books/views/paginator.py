class Paginator():
    """ Makes basic pagination calculations

    Returns:
        Dict: filtered objects
    """
    books_per_pege = 20

    def filter(self, objects_query, page):
        """ Return subset of object

        Args:
            books_query (QuerySet): Entire collection of objects
            page (Int): Number of page

        Returns:
            QuerySet: Subset of objects
        """

        if page < 1:
            return {'books': {}}

        end = page * self.books_per_pege
        start = end - self.books_per_pege
        books_query = objects_query.order_by('title')
        books = books_query[start:end]

        context = {
            'books': books,
        }
        return context

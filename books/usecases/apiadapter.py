from books.models import Category, Book, Author
from books.exceptions import LoadBookException
from books.usecases.apireader import ApiReader


class BookReader():
    """
    Process Google Book API responce,
    creates new objects - Books, Authors, Categories
    """

    def process_request(self, request):
        piece = 40

        end = 0
        foo = 0

        while request.total > request.found:
            begin = foo * piece
            end = min((foo + 1) * piece, request.total)

            try:
                books_json = ApiReader().get_books(
                    request.keywords,
                    begin,
                    end,
                )
            except ConnectionError:
                request.total = request.found
                request.finished = True
                request.error = True
                request.save()
                return

            read_result = BookReader().process_books(books_json, request)

            request.total = read_result["total"]
            request.found += read_result["processed"]
            request.save()

            if read_result["processed"] == 0:
                break

            foo += 1

        request.finished = True
        request.save()

    def process_books(self, books_json, request):
        """ Process full api response

        Args:
            books_json (JSON): Google API response
            request ([type]): Request object foreign key for new books

        Returns:
            Dict: total books number for API request and processed books number
        """
        books = books_json.get("items", [])
        total = books_json.get("totalItems", [])

        for book in books:
            try:
                self.process_book(book, request)
            except LoadBookException:
                pass

        result = {
            'processed': len(books),
            'total': total,
        }
        return result

    def process_book(self, book_json, request):
        """ Process single book json,
        creates Book, Category, Author object if doesn't exist

        Args:
            book_json (JSON): single book json
            request (Request): related request object

        Raises:
            LoadBookException: Obligatory field not found
        """

        volume_id = book_json.get("id", None)
        if not volume_id:
            raise LoadBookException("Volume id not found")

        try:
            Book.objects.get(volume_id=volume_id)
            # Book already in the database
            return
        except Book.DoesNotExist:
            pass

        volume_info = book_json.get("volumeInfo", None)
        if not volume_info:
            raise LoadBookException("Volume info not found")

        title = volume_info.get("title", None)
        if not title:
            raise LoadBookException("Title not found")

        authors = volume_info.get("authors", [])
        if not authors:
            raise LoadBookException("Author not found")

        categories = volume_info.get("categories", [])
        if not categories:
            raise LoadBookException("Category not found")

        description = book_json.get("description", '')
        image = self.get_thumbnail(volume_info)

        new_book = Book()
        new_book.title = title
        new_book.description = description

        if image:
            new_book.google_image_link = image
        new_book.request = request
        new_book.volume_id = volume_id

        new_book.save()
        new_book.authors.add(*self.get_authors_list(authors))
        new_book.categories.add(*self.get_categories_list(categories))
        new_book.save()

    def get_thumbnail(self, volume_info):
        """ Returns link to the largest image from volume_info

        Args:
            volume_info (JSON): volume info JSON

        Returns:
            String: Href to the cover image
        """

        if not volume_info:
            return None

        images = volume_info.get("imageLinks", [])

        if not images:
            return None

        thumbnail = images.get("thumbnail", None)
        small_thumbnail = images.get("smallThumbnail", None)

        if thumbnail:
            return thumbnail
        else:
            return small_thumbnail

    def get_authors_list(self, author_names):
        """
        Process the list of authors names, returns a
        list of corresponding objects, creates new objects
        if don't exist

        Args:
            author_names (List of String): Author names

        Returns:
            List of Athor: Author objects
        """

        authors = []

        for author_name in author_names:
            try:
                author = Author.objects.get(name=author_name)
                authors.append(author)
            except Author.DoesNotExist:
                author = Author()
                author.name = author_name
                author.save()
                authors.append(author)

        return authors

    def get_categories_list(self, categories_names):
        """
        Process the list of categories names, returns a
        list of corresponding objects, creates new objects
        if don't exist

        Args:
            categories_names (List of String): Categories names

        Returns:
            List of Category: Category objects
        """

        categories = []

        for category_name in categories_names:
            try:
                category = Category.objects.get(name=category_name)
                categories.append(category)
            except Category.DoesNotExist:
                category = Category()
                category.name = category_name
                category.save()
                categories.append(category)

        return categories

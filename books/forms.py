from django import forms
from books.models import Author, Book, Category


class BookForm(forms.Form):
    title = forms.CharField(required=True, max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    authors = forms.CharField(
        required=True,
        label="Authors separated by comma",
        widget=forms.TextInput(
            attrs={'placeholder': 'Ben Giladi, Ludwik Finkel...'}
        ),
    )
    categories = forms.CharField(
        required=True,
        label="Categories separated by comma",
        widget=forms.TextInput(
            attrs={'placeholder': 'History, World War, Education...'}
        ),
    )

    image = forms.ImageField(required=False)


class BookCreator():
    """
    Creates the Book object and all related objects
    for given BookForm data
    """

    def save(self, data, request):
        """ Create new Book instance and save

        Args:
            data (BookForm data): Data validated by BookForm
            request (request): Original request with image file
        """

        authors_string = data['authors']
        categories_string = data['categories']

        authors = self.get_authors(authors_string)
        categories = self.get_categories(categories_string)

        new_book = Book()
        new_book.title = data['title']
        new_book.description = data['description']
        new_book.image = request.FILES.get("image", None)
        new_book.save()

        new_book.authors.add(*authors)
        new_book.categories.add(*categories)
        new_book.save()

    def get_authors(self, authors_string):
        """ Get authors object from string names
        sepparated by commas

        Args:
            authors_string (String): names separated by commas

        Returns:
            List of Author: List of author objects
        """

        names = self.separate(authors_string)

        authors = []

        for name in names:
            try:
                author = Author.objects.get(name=name)
                authors.append(author)
            except Author.DoesNotExist:
                author = Author()
                author.name = name
                author.save()
                authors.append(author)

        return authors

    def get_categories(self, categories_string):
        """ Get categories object from string names
        sepparated by commas

        Args:
            categories_string (String): names separated by commas

        Returns:
            List of Categories: List of author objects
        """

        names = self.separate(categories_string)

        categories = []

        for name in names:
            try:
                category = Category.objects.get(name=name)
                categories.append(category)
            except Category.DoesNotExist:
                category = Category()
                category.name = name
                category.save()
                categories.append(category)

        return categories

    def separate(self, string):
        """ Split words sepparateb by commas
        to list

        Args:
            string (String): Separated by commas names

        Returns:
            List of String: names list
        """
        unified = ' '.join(string.split())
        unified = unified.replace(", ", ",")
        unified = unified.replace(" ,", ",")
        names_list = unified.split(",")
        names_list = [x for x in names_list if x]
        return set(names_list)

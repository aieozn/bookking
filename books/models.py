from django.db import models
from books.usecases.apireader import ApiReader


class Request(models.Model):
    """
    Object representing a single API search.
    Allows you to observe the processing progress
    """

    total = models.PositiveIntegerField()
    found = models.PositiveIntegerField(default=0)
    finished = models.BooleanField(default=False)
    keywords = models.TextField()
    error = models.BooleanField(default=False)

    def create(self, keywords):
        """ Init values for the Request object

        Args:
            keywords (String): Search keywords
        """

        self.keywords = keywords

        try:
            self.total = ApiReader().count(keywords)
        except ConnectionError:
            self.total = 0
            self.finished = True
            self.error = True
            self.save()
            return

        if self.total == 0:
            self.finished = True

        self.save()


class Category(models.Model):
    """ Book related category """

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Author(models.Model):
    """ Book related author """

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    """ Book object """

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    authors = models.ManyToManyField(Author)
    categories = models.ManyToManyField(Category)
    image = models.ImageField(
        upload_to='covers',
        default='covers/not_found.png',
        null=True
    )
    google_image_link = models.CharField(max_length=200, null=True, blank=True)
    request = models.ForeignKey(Request, on_delete=models.CASCADE, null=True)
    volume_id = models.CharField(max_length=40, null=True, blank=True)

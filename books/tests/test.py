import mock
import json

from django.test import TestCase
from django.test import Client

from books.views.paginator import Paginator
from books.models import Book, Request, Author, Category
from books.usecases.apireader import ApiReader
from books.usecases.apiadapter import BookReader


class ApiRequestsTests(TestCase):
    """ Test the behaviour of the application
    for different API response scenarios
    """
    empty_scenario = 'books/tests/data/empty_scenario.json'
    tiny_scenartio = 'books/tests/data/tiny_scenario.json'
    large_scenario_1 = 'books/tests/data/long_scenario_1.json'
    large_scenario_2 = 'books/tests/data/long_scenario_2.json'

    requester = 'books.usecases.apireader.ApiReader.make_request'

    def prepare_scenario_data(self, scenario):
        with open(scenario, 'r', encoding="utf8") as outfile:
            data = json.load(outfile)

        return data

    def prepare_empty_mock(self):
        data = self.prepare_scenario_data(self.empty_scenario)
        mocked_get = mock.MagicMock(return_value=data)
        return mocked_get

    def prepare_tiny_mock(self):
        data = self.prepare_scenario_data(self.tiny_scenartio)
        mocked_get = mock.MagicMock(return_value=data)
        return mocked_get

    def prepare_large_mock(self):
        data_1 = self.prepare_scenario_data(self.large_scenario_1)
        data_2 = self.prepare_scenario_data(self.large_scenario_2)

        def my_side_effect(*args, **kwargs):
            start_index = args[0].get("srartIndex", 0)
            if start_index == 0:
                return data_1
            elif start_index == 40:
                return data_2

        mocked_get = mock.MagicMock(side_effect=my_side_effect)
        return mocked_get

    def test_count_api_elements(self):
        with mock.patch(self.requester, self.prepare_empty_mock()):
            res = ApiReader().count('')
            self.assertEqual(res, 0)

        with mock.patch(self.requester, self.prepare_tiny_mock()):
            res = ApiReader().count('')
            self.assertEqual(res, 11)

        with mock.patch(self.requester, self.prepare_large_mock()):
            res = ApiReader().count('')
            self.assertEqual(res, 73)

    def test_request_finished(self):
        with mock.patch(self.requester, self.prepare_empty_mock()):
            request = Request()
            request.create('')
            book_reader = BookReader()
            book_reader.process_request(request)
            self.assertEqual(request.finished, True)

        with mock.patch(self.requester, self.prepare_tiny_mock()):
            request = Request()
            request.create('')
            book_reader = BookReader()
            book_reader.process_request(request)
            self.assertEqual(request.finished, True)

        with mock.patch(self.requester, self.prepare_large_mock()):
            request = Request()
            request.create('')
            book_reader = BookReader()
            book_reader.process_request(request)
            self.assertEqual(request.finished, True)

    def test_save_all_valid_elements(self):
        with mock.patch(self.requester, self.prepare_empty_mock()):
            request = Request()
            request.create('')
            book_reader = BookReader()
            book_reader.process_request(request)
            saved_books = Book.objects.filter(request=request)
            saved_books = len(saved_books)
            self.assertEqual(saved_books, 0)

        with mock.patch(self.requester, self.prepare_tiny_mock()):
            request = Request()
            request.create('')
            book_reader = BookReader()
            book_reader.process_request(request)
            saved_books = Book.objects.filter(request=request)
            saved_books = len(saved_books)
            self.assertEqual(saved_books, 1)

        with mock.patch(self.requester, self.prepare_large_mock()):
            request = Request()
            request.create('')
            book_reader = BookReader()
            book_reader.process_request(request)
            saved_books = Book.objects.filter(request=request)
            saved_books = len(saved_books)
            self.assertEqual(saved_books, 12)

    def test_assign_book_to_existing_author(self):
        with mock.patch(self.requester, self.prepare_large_mock()):
            request = Request()
            request.create('')
            book_reader = BookReader()
            book_reader.process_request(request)
            saved_books = Book.objects.filter(request=request)
            saved_books = len(saved_books)

            ewa = Author.objects.get(name="Ewa Nowacka")
            found = Book.objects.filter(authors=ewa)
            self.assertEqual(len(found), 2)

    def test_assign_book_to_existing_category(self):
        with mock.patch(self.requester, self.prepare_large_mock()):
            request = Request()
            request.create('')
            book_reader = BookReader()
            book_reader.process_request(request)
            saved_books = Book.objects.filter(request=request)
            saved_books = len(saved_books)

            pets = Category.objects.get(name="Pets")
            found = Book.objects.filter(categories=pets)
            self.assertEqual(len(found), 2)


class BookFromTest(TestCase):
    fixtures = ['books']

    def test_valid_data_acceptance(self):
        c = Client()
        c.post(
            '/new/',
            {
                'title': 'Title',
                'description': 'Description',
                'authors': 'Author',
                'categories': 'Category',
            }
        )

        found = Book.objects.filter(title="Title")
        self.assertEqual(len(found), 1)

    def test_invalid_data_rejection(self):
        c = Client()
        c.post(
            '/new/',
            {
                'title': '',
                'description': 'Description',
                'authors': 'Author',
                'categories': 'Category',
            }
        )

        found = Book.objects.filter(title="Title")
        self.assertEqual(len(found), 0)

    def test_assign_book_to_existing_categories(self):
        c = Client()
        c.post(
            '/new/',
            {
                'title': 'Title',
                'description': 'Description',
                'authors': 'Author',
                'categories': 'Art, Computers ,Import quotas',
            }
        )

        found = Book.objects.filter(categories__name="Import quotas")
        self.assertEqual(len(found), 2)

        found = Book.objects.filter(categories__name="Computers")
        self.assertEqual(len(found), 142)

        found = Book.objects.filter(categories__name="Art")
        self.assertEqual(len(found), 3)

    def test_assign_book_to_existing_category(self):
        c = Client()
        c.post(
            '/new/',
            {
                'title': 'Title',
                'description': 'Description',
                'authors': 'Author',
                'categories': 'Art',
            }
        )

        found = Book.objects.filter(categories__name="Art")
        self.assertEqual(len(found), 3)

    def test_assign_book_to_existing_authors(self):
        c = Client()
        c.post(
            '/new/',
            {
                'title': 'Title',
                'description': 'Description',
                'authors': 'Polly Pinder , Al Sweigart',
                'categories': 'Categories',
            }
        )

        found = Book.objects.filter(authors__name="Polly Pinder")
        self.assertEqual(len(found), 2)

        found = Book.objects.filter(authors__name="Al Sweigart")
        self.assertEqual(len(found), 4)

    def test_assign_book_to_existing_author(self):
        c = Client()
        c.post(
            '/new/',
            {
                'title': 'Title',
                'description': 'Description',
                'authors': 'Polly Pinder ,',
                'categories': 'Categories',
            }
        )

        found = Book.objects.filter(authors__name="Polly Pinder")
        self.assertEqual(len(found), 2)


class PaginatorModelTests(TestCase):
    fixtures = ['books']

    def test_search_for_not_existing_page(self):
        data = Book.objects.all()

        # Not existing webpage
        result = Paginator().filter(data, 400)
        self.assertFalse(result["books"])

        # Negative page
        result = Paginator().filter(data, -10)
        self.assertFalse(result["books"])

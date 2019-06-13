# bookking

Simple django application that allows you to discover new books using the Google Books API

# Installing

```
python manage.py makemigrations books
python manage.py migrate
python manage.py runserver
```


# Testing

```
python manage.py test books
```


# Comments

If you see "something went wrong" during search, check if Google Books is available:

```
example: https://www.googleapis.com/books/v1/volumes?q=Hobbit
```

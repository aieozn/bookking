""" Url patterns for main application """
from django.urls import path
from django.conf import settings

from django.conf.urls.static import static

from books.views import views
from books.views import operations

urlpatterns = [
    path('', views.index, name="Home page"),
    path('<int:pagenum>', views.page, name="Books list"),

    path('search/', views.search, name="Search page"),
    path('new/', views.new_book, name="New book form"),

    path('category/<int:id>/', views.index, name="Home page - category"),
    path('category/<int:category_id>/<int:pagenum>', views.category_filtered),

    path('author/<int:id>/', views.index, name="Home page - author"),
    path('author/<int:author_id>/<int:pagenum>', views.author_filtered),

    path('query/<int:id>/', views.index, name="Home page - query"),
    path('query/<int:request_id>/<int:pagenum>', views.request_filtered),

    path('query/', operations.search_init, name="Initialize new search"),
    path('querystatus/<int:id>', operations.search_status, name="Progress"),

    path('clear/', operations.clear, name="Clear database action"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

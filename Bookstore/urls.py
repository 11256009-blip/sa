from django.urls import path

from .views import book_create_view

urlpatterns = [
    path('new/', book_create_view, name='book-create'),
]

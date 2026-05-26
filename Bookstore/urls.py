from django.urls import path

from .views import (
    book_create_view,
    book_delete_view,
    book_edit_view,
    book_list_view,
)

urlpatterns = [
    path('', book_list_view, name='book-list'),
    path('new/', book_create_view, name='book-create'),
    path('<int:pk>/edit/', book_edit_view, name='book-edit'),
    path('<int:pk>/delete/', book_delete_view, name='book-delete'),
]

from django.urls import path

from .views import (
    book_create_view,
    book_delete_view,
    book_edit_view,
    book_list_view,
    borrow_return_view,
    borrow_book_view,
    reserve_book_view,
    return_book_view,
    cancel_reservation_view,
<<<<<<< HEAD
    overdue_management_view,
=======
>>>>>>> e4e8d20e8ac471e1e9abf354dacd46932d0ea566
)

urlpatterns = [
    path('', book_list_view, name='book-list'),
    path('new/', book_create_view, name='book-create'),
    path('borrow-return/', borrow_return_view, name='book-borrow-return'),
<<<<<<< HEAD
    path('overdue/', overdue_management_view, name='overdue-management'),
=======
>>>>>>> e4e8d20e8ac471e1e9abf354dacd46932d0ea566
    path('<int:pk>/borrow/', borrow_book_view, name='book-borrow'),
    path('<int:pk>/reserve/', reserve_book_view, name='book-reserve'),
    path('record/<int:pk>/return/', return_book_view, name='book-return'),
    path('record/<int:pk>/cancel/', cancel_reservation_view, name='book-cancel'),
    path('<int:pk>/edit/', book_edit_view, name='book-edit'),
    path('<int:pk>/delete/', book_delete_view, name='book-delete'),
]

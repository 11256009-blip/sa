from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookForm
from .models import Book


def home_view(request):
    return render(request, 'bookstore/home.html', {
        'user_name': request.user.get_username() or '使用者',
    })


def book_list_view(request):
    query = request.GET.get('q', '').strip()
    books = Book.objects.all()
    if query:
        books = books.filter(Q(isbn__icontains=query) | Q(title__icontains=query))
    books = books.order_by('title')

    return render(request, 'bookstore/book_list.html', {
        'books': books,
        'query': query,
    })


def book_create_view(request):
    form = BookForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('book-list')

    return render(request, 'bookstore/book_form.html', {
        'form': form,
    })


def book_edit_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, instance=book)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('book-list')

    return render(request, 'bookstore/book_form.html', {
        'form': form,
        'book': book,
    })


def book_delete_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book-list')

    return render(request, 'bookstore/book_confirm_delete.html', {
        'book': book,
    })

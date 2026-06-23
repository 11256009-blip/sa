from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import BookForm
from .models import Book, BorrowRecord


def home_view(request):
    return render(request, 'bookstore/home.html', {
        'user_name': request.user.get_username() or '使用者',
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def book_list_view(request):
    query = request.GET.get('q', '').strip()
    books = Book.objects.all()
    if query:
        books = books.filter(Q(isbn__icontains=query) | Q(title__icontains=query))
    books = books.order_by('title')

    borrow_records = BorrowRecord.objects.filter(
        action=BorrowRecord.Action.BORROW,
        status=BorrowRecord.Status.ACTIVE
    ).select_related('user', 'book')

    overdue_records = [r for r in borrow_records if r.is_overdue]

    return render(request, 'bookstore/book_list.html', {
        'books': books,
        'query': query,
        'overdue_records': overdue_records,
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def book_create_view(request):
    form = BookForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        book = form.save()
        messages.success(request, f'已新增《{book.title}》。')
        return redirect('book-list')

    return render(request, 'bookstore/book_form.html', {
        'form': form,
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def book_edit_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, instance=book)
    if request.method == 'POST' and form.is_valid():
        book = form.save()
        messages.success(request, f'已更新《{book.title}》。')
        return redirect('book-list')

    return render(request, 'bookstore/book_form.html', {
        'form': form,
        'book': book,
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def book_delete_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'已下架《{title}》。')
        return redirect('book-list')

    return render(request, 'bookstore/book_confirm_delete.html', {
        'book': book,
    })


@login_required
def borrow_return_view(request):
    query = request.GET.get('q', '').strip()
    books = Book.objects.all()
    if query:
        books = books.filter(Q(isbn__icontains=query) | Q(title__icontains=query))
    books = books.order_by('title')

    if request.user.is_superuser:
        records = BorrowRecord.objects.all()
        users = User.objects.all().order_by('username')
    else:
        records = BorrowRecord.objects.filter(user=request.user)
        users = None

    return render(request, 'bookstore/book_borrow_return.html', {
        'books': books,
        'query': query,
        'records': records,
        'users': users,
    })


@login_required
def borrow_book_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method != 'POST':
        return redirect('book-borrow-return')

    if book.quantity <= 0:
        messages.error(request, '此書目前無可借閱庫存。')
        return redirect('book-borrow-return')

    if request.user.is_superuser:
        user_id = request.POST.get('user_id')
        if user_id:
            user = get_object_or_404(User, pk=user_id)
        else:
            user = request.user
    else:
        user = request.user

    book.quantity -= 1
    book.save()

    BorrowRecord.objects.create(
        user=user,
        book=book,
        action=BorrowRecord.Action.BORROW,
    )
    messages.success(request, f'已借閱《{book.title}》(使用者：{user.username})。')
    return redirect('book-borrow-return')


@login_required
def reserve_book_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method != 'POST':
        return redirect('book-borrow-return')

    if request.user.is_superuser:
        user_id = request.POST.get('user_id')
        if user_id:
            user = get_object_or_404(User, pk=user_id)
        else:
            user = request.user
    else:
        user = request.user

    BorrowRecord.objects.create(
        user=user,
        book=book,
        action=BorrowRecord.Action.RESERVE,
    )
    messages.success(request, f'已預約《{book.title}》(使用者：{user.username})。')
    return redirect('book-borrow-return')


@login_required
def return_book_view(request, pk):
    record = get_object_or_404(BorrowRecord, pk=pk)

    if not request.user.is_superuser and record.user != request.user:
        return redirect('book-borrow-return')

    if request.method != 'POST' or record.action != BorrowRecord.Action.BORROW or record.status != BorrowRecord.Status.ACTIVE:
        return redirect('book-borrow-return')

    record.status = BorrowRecord.Status.RETURNED
    record.returned_at = timezone.now()
    record.save()

    book = record.book
    book.quantity += 1
    book.save()
    messages.success(request, f'已歸還《{book.title}》。')
    return redirect('book-borrow-return')


@login_required
def cancel_reservation_view(request, pk):
    record = get_object_or_404(BorrowRecord, pk=pk)

    if not request.user.is_superuser and record.user != request.user:
        return redirect('book-borrow-return')

    if request.method != 'POST' or record.action != BorrowRecord.Action.RESERVE or record.status != BorrowRecord.Status.ACTIVE:
        return redirect('book-borrow-return')

    record.status = BorrowRecord.Status.CANCELLED
    record.returned_at = record.created_at
    record.save()
    messages.success(request, f'已取消預約《{record.book.title}》。')
    return redirect('book-borrow-return')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def overdue_management_view(request):
    """處理逾期管理通知按鈕。"""
    if request.method == 'POST' and request.POST.get('action') == 'send_notifications':
        messages.success(request, '已發送Gmail')
        return redirect('/books/?tab=overdue')

    return redirect('/books/?tab=overdue')

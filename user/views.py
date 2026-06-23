from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

from .forms import CustomUserChangeForm, CustomUserCreationForm, UserSelfEditForm, UserRegistrationForm


@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_management_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '使用者已成功新增。')
            return redirect('user-root')
    else:
        form = CustomUserCreationForm()

    return render(request, 'user/user_management.html', {
        'form': form,
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_list_view(request):
    users = User.objects.all().order_by('username')
    return render(request, 'user/user_edit_list.html', {
        'users': users,
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_edit_view(request, user_id):
    user_obj = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, '使用者已成功更新。')
            return redirect('user-root')
    else:
        form = CustomUserChangeForm(instance=user_obj)

    return render(request, 'user/user_edit.html', {
        'form': form,
        'edit_user': user_obj,
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_create_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '使用者已成功新增。')
            return redirect('user-create')
    else:
        form = CustomUserCreationForm()

    return render(request, 'user/user_form.html', {'form': form})


def user_login_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    # 支援同頁登入與註冊：根據按鈕 `action` 決定處理路徑
    login_form = AuthenticationForm(request, data=request.POST or None)
    register_form = UserRegistrationForm(request.POST or None)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'login' and login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            return redirect('/')

        if action == 'register' and register_form.is_valid():
            new_user = register_form.save()
            messages.success(request, '註冊成功，已自動登入。')
            login(request, new_user)
            return redirect('/')

    return render(request, 'user/login.html', {
        'form': login_form,
        'register_form': register_form,
        'next': request.GET.get('next', ''),
    })


@login_required
def user_self_edit_view(request):
    if request.method == 'POST':
        form = UserSelfEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '個人資料已更新。')
            return redirect('home')
    else:
        form = UserSelfEditForm(instance=request.user)

    return render(request, 'user/user_self_edit.html', {
        'form': form,
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_delete_view(request, user_id):
    user_obj = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        username = user_obj.username
        user_obj.delete()
        messages.success(request, f'使用者 {username} 已成功刪除。')
        return redirect('user-list')
    
    return render(request, 'user/user_delete.html', {
        'delete_user': user_obj,
    })


def user_logout_view(request):
    logout(request)
    return redirect('/')

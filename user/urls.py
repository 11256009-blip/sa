from django.urls import path

from .views import user_create_view, user_management_view, user_edit_view, user_list_view, user_delete_view

urlpatterns = [
    path('', user_management_view, name='user-root'),
    path('add/', user_create_view, name='user-create'),
    path('list/', user_list_view, name='user-list'),
    path('edit/<int:user_id>/', user_edit_view, name='user-edit'),
    path('delete/<int:user_id>/', user_delete_view, name='user-delete'),
]

//123456
"""
URL configuration for locallibrary project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from Bookstore.views import home_view
from user.views import user_login_view, user_logout_view

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', user_login_view, name='login'),
    path('logout/', user_logout_view, name='logout'),
    path('admin/', admin.site.urls),
    path('books/', include('Bookstore.urls')),
    path('users/', include('user.urls')),
]

from django.conf import settings
from django.conf.urls.static import static
import os

# During development, also serve the app's static directory explicitly
urlpatterns += static(settings.STATIC_URL, document_root=str(settings.BASE_DIR / 'Bookstore' / 'static'))

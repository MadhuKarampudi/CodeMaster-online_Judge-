"""
URL configuration for online_judge_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.http import HttpResponseRedirect
from users import views as user_views

def redirect_to_login(request):
    return HttpResponseRedirect('/auth/login/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_login, name='home'),
    path('auth/login/', user_views.login_view, name='login'),
    path('auth/signup/', user_views.signup_view, name='signup'),
    path('auth/logout/', user_views.logout_view, name='logout'),
]

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
from django.conf import settings
from django.conf.urls.static import static
from problems import views as problem_views
from users import views as user_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

def simple_home(request):
    return HttpResponse("<h1>CodeMaster Online Judge</h1><p>Welcome! <a href='/auth/login/'>Login</a> | <a href='/auth/signup/'>Signup</a></p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', simple_home, name='home'),
    path('auth/login/', user_views.login_view, name='login'),
    path('auth/signup/', user_views.signup_view, name='signup'),
    path('auth/logout/', user_views.logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

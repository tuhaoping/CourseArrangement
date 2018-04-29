"""CourseArrangement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from .views import homePage
from django.contrib.auth.views import login, logout
from app_getcontent.views import get_arrange_table, get_available_place, get_mycourse, test
from .settings import HOME_URL

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'accounts/login/$', login),
    url(r'accounts/logout/$', logout),

    url(r'^home/$', homePage),
    

    url(r'^content/arrange_table/$', get_arrange_table),
    url(r'^content/available_place/$', get_available_place),
    url(r'^mycourse/$', get_mycourse),

    url(r'^test/', test)
]

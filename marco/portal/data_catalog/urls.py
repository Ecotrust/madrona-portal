# from django.conf.urls import url, patterns
from django.urls import re_path, include
from . import views

urlpatterns = [
    #'',
    re_path(r'^$', views.catalog),
    re_path(r'^([A-Za-z0-9_-]+)/$', views.theme),
]

from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('type', views.catalog_type, name='catalog_type'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('catalog/', views.catalog_list, name='catalog'),
]

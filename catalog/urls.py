from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('catalog/', views.catalog_list, name='catalog'),
    path('catalog/<int:pk>/', views.cake_detail, name='cake_detail'),
    path('about/', views.about_page, name='about'),
]

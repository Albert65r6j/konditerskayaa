from django.urls import path
from . import views

urlpatterns = [
    path('constructor/', views.order_constructor, name='constructor'),
    path('my/', views.my_orders, name='my_orders'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('schedule/', views.kitchen_schedule, name='kitchen_schedule'),
]

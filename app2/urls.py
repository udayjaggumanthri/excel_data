from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.home2, name='home2'),
] 
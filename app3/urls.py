from django.urls import path
from . import views

app_name = 'app3'

urlpatterns = [
    path('home3/', views.home3, name='home3'),
] 
from django.contrib import admin
from django.urls import path, include
from app import views as app_views
from app2 import views as app2_views
from app3 import views as app3_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', app_views.home, name='home'),
    path('results/', app_views.results, name='results'),
    path('home2/', app2_views.home2, name='home2'),
    path('app3/', include('app3.urls')),
] 
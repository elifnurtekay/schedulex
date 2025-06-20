
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('', views.index, name='index'),
    path('dersler/', views.ders_list, name='ders_list'),
    path('ders_ekle/', views.ders_ekle, name='ders_ekle'),
    path('program_olustur/', views.program_olustur, name='program_olustur'),
    path('program/', views.program_goruntule, name='program_goruntule'),
    path('derslik_ekle/', views.derslik_ekle, name='derslik_ekle'),
    path('derslikler/', views.derslik_list, name='derslik_list'),
    path('program_sinif/', views.program_goruntule_sinif, name='program_goruntule_sinif'),
]

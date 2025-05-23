from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('ejemplo/', views.ejemplo, name='ejemplo'),
    path('search-stock/', views.search_stock, name='search_stock'),

]

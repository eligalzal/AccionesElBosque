from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('search-stock/', views.search_stock, name='search_stock'),
    path('change_plan/', views.change_plan, name='change_plan'),
    path('', views.homepage, name='homepage'),

]

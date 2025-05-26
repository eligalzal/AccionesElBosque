from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('perfil/', views.perfil, name='perfil'),
    path('crear_sesion_stripe/', views.crear_sesion_stripe, name='crear_sesion_stripe'),
    path('finalizar_registro/', views.finalizar_registro, name='finalizar_registro'),

    ]


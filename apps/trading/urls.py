from django.urls import path
from . import views

urlpatterns = [
    path('comprar/', views.comprar, name='comprar'),
    path('vender/', views.vender, name='vender'),
    path('portafolio/', views.portafolio, name='portafolio'),

    path('orden_resultado/', views.orden_resultado, name='orden_resultado'),

]
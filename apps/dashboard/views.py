from django.shortcuts import render
from .finnhub_api import *

def dashboard(request):
    simbolo = 'AAPL'
    datos = obtener_precio_accion(simbolo)
    print(f"s: {simbolo}, d:{datos}")
    noticias = obtener_market_news('AAPL')
    print(f"not: {noticias}")
    return render(request, 'dashboard/dashboard.html')

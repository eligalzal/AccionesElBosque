from django.shortcuts import render, redirect

from .finnhub_api import *
from django.db import connection
from django.http import JsonResponse
import json
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def homepage(request):
    
    return render(request, "dashboard/homepage.html")



def search_stock(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ticker = data.get('ticker', '').upper().strip()
            
            if not ticker:
                return JsonResponse({'error': 'Ticker es requerido'}, status=400)
            
            stock_info = get_stock_data(ticker)
            
            detailed_info = obtener_datos_finnhub(ticker)
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT nombre FROM intereses WHERE ticker = %s
                """, (ticker,))
                result = cursor.fetchone()
                stock_name = result[0] if result else ticker
            
            response_data = {
                'ticker': ticker,
                'name': stock_name,
                'price': stock_info.get('price', 'N/A'),
                'change': stock_info.get('change', 'N/A'),
                'open': detailed_info.get('open', 'N/A') if detailed_info else 'N/A',
                'high': detailed_info.get('high', 'N/A') if detailed_info else 'N/A',
                'low': detailed_info.get('low', 'N/A') if detailed_info else 'N/A',
                'prev_close': detailed_info.get('prev_close', 'N/A') if detailed_info else 'N/A',
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'error': f'Error al buscar el ticker: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def dashboard(request): 
    usuario = request.session.get('username')
    stocks_data = []

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT interest1, interest2, interest3, saldo, plan
            FROM usuarios
            WHERE username = %s
        """, (usuario,))
        intereses = cursor.fetchone()

        if intereses is None:
            return render(request, 'dashboard/dashboard.html', {
                "error": "No se encontraron intereses para este usuario."
            })

        tickers = [intereses[0], intereses[1], intereses[2]]
        saldo = intereses[3]
        plan = intereses[4]

        formato = ','.join(['%s'] * len(tickers))
        cursor.execute(f"""
            SELECT ticker, nombre
            FROM intereses
            WHERE ticker IN ({formato})
        """, tickers)

        filas = cursor.fetchall()
        nombres_ticker = {row[0]: row[1] for row in filas}

        cursor.execute(f"""
            SELECT ticker, nombre
            FROM intereses
            WHERE ticker NOT IN ({formato})
            ORDER BY RAND()
            LIMIT 1
        """, tickers)
        
        random_row = cursor.fetchone()
        ticker_aleatorio = None
        if random_row:
            ticker_aleatorio = {
                "ticker": random_row[0],
                "name": random_row[1]
            }

    for ticker in tickers:
        try:
            info = get_stock_data(ticker)
            info['name'] = nombres_ticker.get(ticker, ticker)

            stocks_data.append(info)
            
        except Exception as e:
            print(f"Error al obtener datos para {ticker}: {e}")
    watchlist_data = []
    for ticker in tickers:
        try:
            info = obtener_datos_finnhub(ticker)
            if info:
                info['ticker'] = ticker
                info['name'] = nombres_ticker.get(ticker, ticker)
                watchlist_data.append(info)
        except Exception as e:
            print(f"Error al obtener datos para watchlist de {ticker}: {e}")
    random_stock = None
    if ticker_aleatorio:
        try:
            data = get_stock_data(ticker_aleatorio['ticker'])
            data['name'] = ticker_aleatorio['name']
            random_stock = data
        except Exception as e:
            print(f"Error al obtener datos para ticker aleatorio: {e}")

    return render(request, 'dashboard/dashboard.html', {
        "stocks": stocks_data,
        "random_stock": random_stock,
        "watchlist": watchlist_data,
        "saldo": saldo,  
        "plan": plan,
    })



def change_plan(request): 
    usuario = request.session.get('username')
    plan = request.session.get("selected_plan")  
    pago_status = request.GET.get("pago")  

    if pago_status == "exito" and plan:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE usuarios SET plan = %s WHERE username = %s", [plan, usuario])
        del request.session["selected_plan"]  

    if request.method == "POST":
        plan = request.POST.get('plan')

        if plan in ["Mensual", "Anual"]:
            request.session["selected_plan"] = plan  
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": 1200 if plan == "Mensual" else 12000,
                        "product_data": {
                            "name": plan,
                        },
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=request.build_absolute_uri(request.path) + '?pago=exito',
                cancel_url=request.build_absolute_uri(request.path) + '?pago=fallido',
            )
            return redirect(session.url, code=303)

        elif plan == "free":
            with connection.cursor() as cursor:
                cursor.execute("UPDATE usuarios SET plan = %s WHERE username = %s", [plan, usuario])
            return redirect("dashboard")  
    return render(request, "dashboard/dashboard.html")


    

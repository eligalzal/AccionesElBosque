from ..accounts.alpaca_utils import *  
from django.shortcuts import render
from django.db import connection
from ..dashboard.finnhub_api import *
from django.shortcuts import render, redirect
from django.core.mail import send_mail


def portafolio(request):
    usuario = request.session.get('username')

    with connection.cursor() as cursor:
        cursor.execute("SELECT alpaca_id, saldo FROM usuarios WHERE username = %s", (usuario,))
        info = cursor.fetchone()

    if not info:
        return render(request, 'trading/orden_resultado.html', {'resultado': 'Usuario no encontrado'})

    alpaca_id = info[0]
    saldo = info[1]

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT symbol, SUM(CASE WHEN tipo = 'buy' THEN qty ELSE -qty END) AS qty
            FROM ordenes
            WHERE alpaca_id = %s
            GROUP BY symbol
            HAVING qty > 0
        """, (alpaca_id,)) 
        posiciones = cursor.fetchall()


    portafolio = []
    for symbol, cantidad in posiciones:
        precio_actual = obtener_precio_actual(symbol)
        valor_total = Decimal(precio_actual) * cantidad if precio_actual else None
        portafolio.append({
            'symbol': symbol,
            'cantidad': cantidad,
            'precio_actual': precio_actual,
            'valor_total': valor_total,
            
        })

    return render(request, 'trading/portafolio.html', {'portafolio': portafolio, 'saldo': saldo})


def vender(request): 
    usuario = request.session.get('username')

    with connection.cursor() as cursor:
        cursor.execute("SELECT alpaca_id FROM usuarios WHERE username = %s", (usuario,))
        info = cursor.fetchone()

    if not info:
        return render(request, 'trading/orden_resultado.html', {
            'resultado': {'status': 'error', 'error': 'Usuario no encontrado'}
        })

    alpaca_id = info[0]

    if request.method == 'POST':
        symbol = request.POST['symbol']
        qty = int(request.POST['qty'])

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT cantidad FROM portafolio 
                WHERE alpaca_id = %s AND symbol = %s
            """, (alpaca_id, symbol))
            resultado = cursor.fetchone()

        if not resultado or resultado[0] < qty:
            return render(request, 'trading/orden_resultado.html', {
                'resultado': {
                    'status': 'error',
                    'error': f"No tienes suficientes acciones de {symbol} para vender.",
                    'symbol': symbol,
                    'qty': qty
                }
            })

        resultado_orden = place_market_order(alpaca_id, symbol, qty, 'sell')
        order_id = resultado_orden.get('order_id')
        estado = resultado_orden.get('status')
        fills = resultado_orden.get('data', {}).get('fills', [])

        if not order_id:
            return render(request, 'trading/orden_resultado.html', {
                'resultado': {
                    'status': 'error',
                    'error': f"Error creando la orden: {resultado_orden}",
                    'symbol': symbol,
                    'qty': qty
                }
            })

        precio_unitario = None
        total = None
        if estado == 'filled' and fills:
            precio_unitario = sum(Decimal(f['price']) * Decimal(f['qty']) for f in fills) / sum(Decimal(f['qty']) for f in fills)
            total = sum(Decimal(f['price']) * Decimal(f['qty']) for f in fills)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ordenes (order_id, alpaca_id, symbol, qty, tipo, estado, precio_unitario, total)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                order_id, alpaca_id, symbol, qty, 'sell', estado,
                round(precio_unitario, 2) if precio_unitario else None,
                round(total, 2) if total else None
            ))

        if estado != 'filled':
            time.sleep(5)
            sincronizar_ordenes(alpaca_id)

        with connection.cursor() as cursor:
            cursor.execute("SELECT estado, total FROM ordenes WHERE order_id = %s", (order_id,))
            orden = cursor.fetchone()

        estado_final = orden[0]
        total_final = orden[1]

        if estado_final == 'filled' and total_final is not None:
            ok, nuevo_saldo = actualizar_saldo(alpaca_id, total_final * Decimal('0.98'), sumar=True)
            if not ok:
                return render(request, 'trading/orden_resultado.html', {
                    'resultado': {
                        'status': 'error',
                        'error': f"Orden completada pero error actualizando saldo: {nuevo_saldo}",
                        'order_id': order_id,
                        'symbol': symbol,
                        'qty': qty
                    }
                })
            with connection.cursor() as cursor:
                cursor.execute("SELECT first_name, email FROM usuarios WHERE username = %s", [usuario])
                user_info = cursor.fetchone()
                nombre_usuario = user_info[0]
                email_usuario = user_info[1]

            send_mail(
                "¡Venta de acción completada!",
                f"Hola {nombre_usuario},\n\nTu orden de venta ha sido completada exitosamente.\n\nAcción: {symbol}\nCantidad: {qty}\nMonto total recibido: ${total_final:.2f}\n\nGracias por operar con Acciones El Bosque.",
                "elianita.galban@gmail.com", 
                [email_usuario, 'egalbanz@unbosque.edu.co'],
                fail_silently=False
            )
            return render(request, 'trading/orden_resultado.html', {
                'resultado': {
                    'status': 'filled',
                    'order_id': order_id,
                    'symbol': symbol,
                    'qty': qty,
                    'side': 'sell',
                    'filled_price': round(total_final / qty, 2),
                    'total_value': round(total_final, 2)
                },
                'estados_pendientes': ['pending', 'new', 'accepted', 'pending_new']
            })

        return render(request, 'trading/orden_resultado.html', {
            'resultado': {
                'status': estado_final,
                'order_id': order_id,
                'symbol': symbol,
                'qty': qty
            },
            'estados_pendientes': ['pending', 'new', 'accepted', 'pending_new']
        })

    return redirect('portafolio')



from decimal import Decimal

def comprar(request):
    usuario = request.session.get('username')
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT alpaca_id FROM usuarios WHERE username = %s", (usuario,))
        info = cursor.fetchone()
    
    if not info:
        return render(request, 'trading/orden_resultado.html', {'resultado': 'Usuario no encontrado'})
    
    alpaca_id = info[0]
    
    if request.method == 'POST':
        symbol = request.POST['symbol']
        qty = int(request.POST['qty'])
        precio_actual = obtener_precio_actual(symbol)

        resultado_orden = place_market_order(alpaca_id, symbol, qty, 'buy')
        print(resultado_orden)

        if resultado_orden:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO ordenes (order_id, alpaca_id, symbol, qty, tipo, estado)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (resultado_orden.get('order_id'), alpaca_id, symbol, qty, 'buy', resultado_orden.get('status')))

        print(resultado_orden)

        time.sleep(5)
        sincronizar_ordenes(alpaca_id)

        with connection.cursor() as cursor:
            cursor.execute("SELECT estado FROM ordenes WHERE order_id = %s", (resultado_orden.get('order_id'),))
            estatus = cursor.fetchone()[0]

        print(estatus)

        if estatus == 'filled':
            total_pagado = 0
            for fill in resultado_orden.get('fills', []):
                total_pagado += (Decimal(fill['qty']) * Decimal(fill['price']))

            ok, msg = actualizar_saldo(alpaca_id, (total_pagado + (total_pagado*0.02)))
            with connection.cursor() as cursor:
                cursor.execute("SELECT first_name, email FROM usuarios WHERE username = %s", [usuario])
                user_info = cursor.fetchone()
                nombre_usuario = user_info[0]
                email_usuario = user_info[1]

            send_mail(
                "¡Compra de acción exitosa!",
                f"Hola {nombre_usuario},\n\nTu orden de compra ha sido completada exitosamente.\n\nAcción: {symbol}\nCantidad: {qty}\nPrecio total: ${total_pagado:.2f}\n\nGracias por invertir con Acciones El Bosque.",
                "elianita.galban@gmail.com",  
                [email_usuario, 'egalbanz@unbosque.edu.co'],
                fail_silently=False
            )

            if not ok:
                return render(request, 'trading/orden_resultado.html', {
                    'resultado': f"Orden filled pero error descontando saldo: {msg}"
                })
            else:
                return render(request, 'trading/orden_resultado.html', {
                    'resultado': f"Orden filled. Saldo actualizado. Nuevo saldo: {msg}",
                    'precio_actual': precio_actual,
                    'symbol': symbol
                })

        return render(request, 'trading/orden_resultado.html', {
            'resultado': resultado_orden,
            'qty': str(qty),
            'estados_pendientes': ["pending", "pending_new", "new", "accepted"],
            'precio_actual': obtener_precio_actual(symbol),
            'symbol': symbol
        })

    symbol_prefill = request.GET.get('symbol', '')
    precio_actual = obtener_precio_actual(symbol_prefill) if symbol_prefill else None
    
    return render(request, 'trading/comprar.html', {
        'symbol_prefill': symbol_prefill,
        'precio_actual': precio_actual
    })

def orden_resultado(request):

    return render(request, "trading/orden_resultado.html")
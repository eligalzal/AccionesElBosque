from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from .alpaca_utils import *  
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
import logging
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

def register(request):
    pago_status = request.GET.get("pago")  

    if pago_status == "exito":
        user_data = request.session.get("user_data")
        
        if user_data:
            return finalizar_registro(request, user_data)
        else:
            messages.error(request, "No se pudo completar el registro. Sesión expirada.")
            return redirect("register")
    elif pago_status == "fallido":
        messages.warning(request, "El pago fue cancelado.")

    if request.method == "POST":
        user_data = {
            "username": request.POST.get("username"),
            "passw": make_password(request.POST.get("password1")),
            "email": request.POST.get("email"),
            "first_name": request.POST.get("first_name"),
            "last_name": request.POST.get("last_name"),
            "street_address": request.POST.get("street_address"),
            "phone_number": request.POST.get("phone_number"),
            "date_of_birth": request.POST.get("date_of_birth"),
            "interest1": request.POST.get("interest1"),
            "interest2": request.POST.get("interest2"),
            "interest3": request.POST.get("interest3"),
            "plan": request.POST.get("plan"),
        }
    
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = %s",[user_data["username"]])
            if cursor.fetchone()[0] > 0:
                messages.error(request, "El nombre de usuario ya está en uso. Por favor elige otro.")
                return render(request, "accounts/register.html", {"form_data": request.POST})
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = %s",[user_data["email"]])
            if cursor.fetchone()[0] > 0:
                messages.error(request, "El correo registrado ya está en uso. Por favor elige otro.")
                return render(request, "accounts/register.html", {"form_data": request.POST})

        if user_data["plan"] in ["Mensual", "Anual"]:
            request.session["user_data"] = user_data
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": 1200 if user_data["plan"] == "Mensual" else 12000,
                        "product_data": {
                            "name": "Mensual" if user_data["plan"] == "Mensual" else "Anual",
                        },
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=request.build_absolute_uri(request.path) + '?pago=exito',
                cancel_url=request.build_absolute_uri(request.path) + '?pago=fallido',
            )
            return redirect(session.url, code=303)

        return finalizar_registro(request, user_data)

    return render(request, "accounts/register.html")


def finalizar_registro(request, user_data):
    resultado = create_alpaca_broker_account(
        email=user_data["email"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        street_address=user_data["street_address"],
        phone_number=user_data["phone_number"],
        date_of_birth=user_data["date_of_birth"],
    )

    if resultado["success"]:
        alpaca_id = resultado["alpaca_id"]

        alpaca_response = create_ach(alpaca_id)
        print(f"ALPACA_RESPONSE --------------------------------------{alpaca_response}")

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO usuarios 
                (username, passw, email, first_name, last_name, street_address, phone_number, date_of_birth, interest1, interest2, interest3, plan, alpaca_id, tr_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                user_data["username"], user_data["passw"], user_data["email"],
                user_data["first_name"], user_data["last_name"], user_data["street_address"],
                user_data["phone_number"], user_data["date_of_birth"], user_data["interest1"],
                user_data["interest2"], user_data["interest3"], user_data["plan"], alpaca_id, alpaca_response
            ])

        messages.success(request, "¡Usuario registrado y cuenta Alpaca creada!")

        send_mail(
            "Acciones El Bosque te da la bienvenida",
            f"Hola {user_data['first_name']},\n\n¡Bienvenido(a) a Acciones El Bosque! Estamos muy felices de que te unas a nuestra comunidad.\n\nTu cuenta se ha creado exitosamente...",
            "elianita.galban@gmail.com",
            [user_data["email"], 'egalbanz@unbosque.edu.co'],
            fail_silently=False
        )

    return redirect("login")


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        with connection.cursor() as cursor:
            cursor.execute("SELECT passw, first_name, last_name, email FROM usuarios WHERE username = %s;", [username])
            user = cursor.fetchone()

        if user:
            hashed_password, first_name, last_name, email = user
            if check_password(password, hashed_password):
                request.session['first_name'] = first_name
                request.session['last_name'] = last_name
                request.session['username'] = username
                request.session['email'] = email

                
                messages.success(request, 'Login exitoso.')

                
                return redirect('dashboard')
            else:
                messages.error(request, 'Contraseña incorrecta.')
        else:
            messages.error(request, 'Usuario no encontrado.')

    return render(request, 'accounts/login.html')

def perfil(request):
    username = request.session.get('username')

    if not username:
        return redirect('login')  
    with connection.cursor() as cursor:
        cursor.execute("SELECT first_name, last_name, email, plan, saldo FROM usuarios WHERE username = %s;", [username])
        user = cursor.fetchone()
        first_name, last_name, email, plan, saldo = user

    pago_status = request.GET.get("pago")
    monto = request.session.get("monto_pago")  
    with connection.cursor() as cursor:
        cursor.execute("SELECT alpaca_id, tr_id FROM usuarios WHERE username = %s;", [username])
        info = cursor.fetchone()
        alpaca_id = info[0]
        tr_id = info[1]

    alpaca_response = transfer(alpaca_id, monto, tr_id)



    if pago_status == "exito" and monto:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE usuarios SET saldo = saldo + %s WHERE username = %s", [monto, username])

        alpaca_response = transfer(alpaca_id, monto, tr_id)

        print(alpaca_response)

        send_mail(
        "¡Eres oficialmente premium!",
        f"Hola {first_name},\n\nTu recarga de ${monto} ha sido procesada exitosamente y tu plan actual es {plan}.\n\n¡Gracias por confiar en nosotros!\n\nEquipo Acciones El Bosque",
        "elianita.galban@gmail.com",  
        [email, 'egalbanz@unbosque.edu.co'],  
        fail_silently=False
    )

        del request.session["monto_pago"]  

    elif pago_status == "fallido":
        messages.warning(request, "El pago fue cancelado o fallido.")

    if request.method == "POST":
        try:
            monto = float(request.POST.get("depositAmount"))
            request.session["monto_pago"] = monto  
            
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(monto * 100),  
                        "product_data": {
                            "name": f"Recarga de saldo: ${monto}",
                        },
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=request.build_absolute_uri(request.path) + '?pago=exito',
                cancel_url=request.build_absolute_uri(request.path) + '?pago=fallido',
            )
            return redirect(session.url, code=303)
        except Exception as e:
            messages.error(request, f"Error al iniciar pago: {str(e)}")

    return render(request, 'accounts/perfil.html', {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "plan": plan,
        "saldo": saldo
    })

#def perfil(request):
#    return render(request, 'accounts/perfil.html', {
#        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
#    })

@csrf_exempt
def crear_sesion_stripe(request, monto):
    
    monto = float('monto')

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                "unit_amount": int(monto * 100), 
                'product_data': {
                    'name': 'Suscripción Mensual',
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:8000/accounts/perfil/?pago=exitoso',
        cancel_url='http://localhost:8000/accounts/perfil/?pago=cancelado',
        metadata={"user_id": request.user.id, "monto": monto}
    )
    return redirect(session.url, code=303)
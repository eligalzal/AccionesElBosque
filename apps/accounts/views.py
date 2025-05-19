from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from .alpaca_utils import create_alpaca_broker_account  
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        passw = make_password(request.POST.get("password1"))  
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        street_address = request.POST.get("street_address")
        phone_number = request.POST.get("phone_number")
        date_of_birth = request.POST.get("date_of_birth")
        interest1 = request.POST.get("interest1")
        interest2 = request.POST.get("interest2")
        interest3 = request.POST.get("interest3")

        
        create_alpaca_broker_account(
            email=email,
            first_name=first_name,
            last_name=last_name,
            street_address=street_address,
            phone_number=phone_number,
            date_of_birth=date_of_birth,
        )

        
        with connection.cursor() as cursor:
            cursor.execute("""
                    INSERT INTO usuarios (username, passw, email, first_name, last_name, street_address, phone_number, date_of_birth, interest1, interest2, interest3)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [username, passw, email, first_name, last_name, street_address, phone_number, date_of_birth, interest1, interest2, interest3])
        messages.success(request, "¡Usuario registrado y cuenta Alpaca creada!")

        send_mail(
                    f"Acciones El Bosque te da la bienvenida",
                    f"Hola {first_name},\n\n¡Bienvenido(a) a Acciones El Bosque! Estamos muy felices de que te unas a nuestra comunidad.\n\nTu cuenta se ha creado exitosamente, y ahora puedes acceder a nuestra plataforma para comenzar a disfrutar del trading con nosotros.\n\nSi tienes alguna pregunta o necesitas ayuda, no dudes en responder a este correo.\n\nGracias por tu confianza.\n\nSaludos cordiales,\nEl equipo de Acciones El Bosque",
                    "elianita.galban@gmail.com",
                    [email, 'egalbanz@unbosque.edu.co'],
                    fail_silently = False
                )
        return redirect("login")
    
    return render(request, "accounts/register.html")


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

                send_mail(
                    "Acciones El Bosque te da la bienvenida",
                    f"Hola {first_name},\n\n¡Bienvenido(a) a Acciones El Bosque! Estamos muy felices de que te unas a nuestra comunidad.\n\nTu cuenta se ha creado exitosamente, y ahora puedes acceder a nuestra plataforma para comenzar a disfrutar del trading con nosotros.\n\nSi tienes alguna pregunta o necesitas ayuda, no dudes en responder a este correo.\n\nGracias por tu confianza.\n\nSaludos cordiales,\nEl equipo de Acciones El Bosque",
                    "elianita.galban@gmail.com",
                    ['c2016027@gmail.com'],
                    fail_silently = False
                )
                return redirect('dashboard')
            else:
                messages.error(request, 'Contraseña incorrecta.')
        else:
            messages.error(request, 'Usuario no encontrado.')

    return render(request, 'accounts/login.html')

def perfil(request):
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    return render(request, 'accounts/perfil.html')
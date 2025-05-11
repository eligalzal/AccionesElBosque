# views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Usuarios
from .alpaca_utils import create_alpaca_broker_account
from .forms import CustomUserCreationForm

def register(request): 
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            result = create_alpaca_broker_account(
                user=None,
                email=cd["email"],
                first_name=cd["first_name"],
                last_name=cd["last_name"],
                street_address=cd["street_address"],
                phone_number=cd["phone_number"],
                date_of_birth=cd["date_of_birth"]
            )

            if result["success"]:
                Usuarios.objects.create(
                    username=cd["username"],
                    email=cd["email"],
                    first_name=cd["first_name"],
                    last_name=cd["last_name"],
                    street_address=cd["street_address"],
                    phone_number=cd["phone_number"],
                    date_of_birth=cd["date_of_birth"],
                    interest1=cd["interest1"],
                    interest2=cd["interest2"],
                    interest3=cd["interest3"],
                    alpaca_account_id=result["account_id"],
                    kyc_status=result["kyc_status"]
                )
                messages.success(request, "¡Usuario registrado y cuenta Alpaca creada!")
            else:
                messages.error(request, f"Error con Alpaca: {result['error']}")
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/register.html", {"form": form})

def login(request):
    return render(request, 'accounts/login.html')

def perfil(request):
    return render(request, 'accounts/perfil.html')
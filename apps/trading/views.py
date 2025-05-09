# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import AlpacaBrokerAccount
from .alpaca_utils import create_alpaca_broker_account  # Función para crear cuenta en Alpaca
from .forms import CustomUserCreationForm

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get("email")
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")

            result = create_alpaca_broker_account(user, email, first_name, last_name)

            if result["success"]:
                AlpacaBrokerAccount.objects.create(
                    user=user,
                    alpaca_account_id=result["account_id"],
                    email=email,
                    kyc_status=result["kyc_status"]
                )
                messages.success(request, "✅ Registro y cuenta Alpaca creados.")
            else:
                messages.error(request, f"❌ Error al crear cuenta Alpaca: {result['error']}")
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "trading/register.html", {"form": form})

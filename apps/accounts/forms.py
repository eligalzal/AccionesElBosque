from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    street_address = forms.CharField(required=True)
    phone_number = forms.IntegerField(required=True)
    date_of_birth = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    interest1 = forms.CharField(required=True)
    interest2 = forms.CharField(required=True)
    interest3 = forms.CharField(required=True)


    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2", "street_address", "phone_number", "date_of_birth", "interest1", "interest2", "interest3")
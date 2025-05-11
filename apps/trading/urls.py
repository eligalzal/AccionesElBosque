from django.urls import path
from django.http import HttpResponse

def test_view(request):
    return HttpResponse("¡Funciona!")

urlpatterns = [
    path('', test_view),
]
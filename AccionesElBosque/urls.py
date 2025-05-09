from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home_view(request):
    return HttpResponse("owo")

urlpatterns = [
    path('', home_view), 
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('trading/', include('apps.trading.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('logs/', include('apps.logs.urls')),
]

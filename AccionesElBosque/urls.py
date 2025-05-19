from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

urlpatterns = [
    path('accounts/', include('apps.accounts.urls')),
    path('trading/', include('apps.trading.urls')),
    path('', include('apps.dashboard.urls')),
]

from django.urls import path
from .api_views import *

urlpatterns = [
    path('usuarios/', usuarios, name="usuarios"),
    path('lista_albumes/<str:nombre_usuario>/', lista_albumes_usuario, name='lista_albumes'),
]
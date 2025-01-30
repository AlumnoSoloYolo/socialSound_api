from django.urls import path
from .api_views import *

urlpatterns = [
    path('usuarios/', usuarios, name="usuarios"),
    path('<str:nombre_usuario>/albumes', lista_albumes_usuario, name='lista_albumes'),
    path('usuarios/lista_usuarios_completa/', lista_usuarios_completa, name="lista_usuarios_completa")
]
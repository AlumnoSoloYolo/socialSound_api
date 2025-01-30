from django.urls import path
from .api_views import *

urlpatterns = [
    path('playlists/', lista_playlists, name="lista_playlists"),
    path('<str:nombre_usuario>/albumes/', lista_albumes_usuario, name='lista_albumes'),
    path('usuarios/lista_usuarios_completa/', lista_usuarios_completa, name="lista_usuarios_completa"),
    path('canciones/lista_canciones_completa/', lista_canciones_completa, name="lista_canciones_completa"),
    path('canciones/generos/', canciones_por_genero, name='canciones_por_genero')
]
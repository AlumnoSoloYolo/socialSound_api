from django.urls import path
from .api_views import *

urlpatterns = [
    path('playlists/', lista_playlists, name="lista_playlists"),
    path('<str:nombre_usuario>/albumes/', lista_albumes_usuario, name='lista_albumes'),
    path('usuarios/lista_usuarios_completa/', lista_usuarios_completa, name="lista_usuarios_completa"),
    path('canciones/lista_canciones_completa/', lista_canciones_completa, name="lista_canciones_completa"),
    path('canciones/generos/', canciones_por_genero, name='canciones_por_genero'),

    path('usuarios/busqueda_simple', usuario_buscar, name='busqueda_usuarios'),
    path('usuarios/busqueda_avanzada/', usuario_busqueda_avanzada),
    path('albumes/busqueda_avanzada/', album_busqueda_avanzada),
    path('canciones/busqueda_avanzada/', cancion_busqueda_avanzada),
    path('playlists/busqueda_avanzada/', playlist_busqueda_avanzada),

    path('usuarios/crear', usuario_create),


]
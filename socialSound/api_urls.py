from django.urls import path
from .api_views import *
from rest_framework.routers import DefaultRouter
from .api_views import UsuarioViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')

urlpatterns = [
    path('playlists/', lista_playlists, name="lista_playlists"),
     path('albumes/', lista_albumes, name='lista_albumes_completa'),
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
    path('usuarios/<int:id>', usuario_detail),
    path('usuarios/<int:id>/actualizar', usuario_update),
    path('usuarios/actualizar/nombre/<int:usuario_id>', usuario_actualizar_nombre, name='usuario_actualizar_nombre'),
    path('usuarios/eliminar/<int:usuario_id>', usuario_eliminar),
    path('albumes/', album_list, name='album-list'),
    path('albumes/<int:album_id>/detalles/', detalle_album_create, name='crear_detalle_album'),
    path('usuarios/', usuario_list, name="lista-usuarios"),
    path('albumes/crear/', album_crear, name='album-crear'),
    path('albumes/<int:id>/', album_detail),  
    path('albumes/<int:id>/editar/', album_update),  
    path('albumes/actualizar/titulo/<int:id>/', album_patch_titulo),
    path('albumes/<int:id>/eliminar/', album_delete),
    path('playlists/crear/', playlist_create),
    path('canciones/', obtener_canciones, name='lista_canciones'),
    path('playlists/<int:id>/', playlist_detail, name='playlist_detail'),
    path('playlists/<int:id>/editar/', playlist_update, name='playlist_update'),
    path('playlists/<int:id>/actualizar/canciones/', playlist_patch_canciones),
    path('playlists/<int:id>/eliminar/', playlist_delete),
    path('cancion-playlist/crear/', cancion_playlist_create),
    path('likes/crear/', like_create),
    path('likes/eliminar/', like_delete),




    path('albumes/detalles/<int:id>/', detalle_album_detail),  
    path('albumes/detalles/<int:id>/editar/', detalle_album_update),



]
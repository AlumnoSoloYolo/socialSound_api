from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from .import views
from .forms import CustomSetPasswordForm

urlpatterns = [
     path('registro/', views.registro_usuario, name='registro_usuario'),
     path('login/', views.login_usuario, name='login_usuario'),
     path('logout/', views.logout_view, name='logout'),
     path('perfil/<str:nombre_usuario>/actualizar/', views.actualizar_perfil, name='actualizar_perfil'),
     path('perfil/<str:nombre_usuario>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
     path('usuarios/busqueda-avanzada/', views.busqueda_avanzada_usuarios, name='busqueda_avanzada_usuarios'),
     path('seguir/<int:usuario_id>/', views.seguir_usuario, name='seguir_usuario'),
     path('dejar-de-seguir/<int:usuario_id>/', views.dejar_de_seguir_usuario, name='dejar_de_seguir_usuario'),
     # path('perfil/<str:nombre_usuario>/album/crear/', views.crear_album, name='crear_album'),
     path('perfil/<str:nombre_usuario>/album/<int:album_id>/editar/', views.editar_album, name='editar_album'),
     path('album/busqueda-avanzada/', views.busqueda_avanzada_album, name='busqueda_avanzada_albumes'),
     path('album/<int:album_id>/eliminar/', views.eliminar_album, name='eliminar_album'),
     path('album/<int:album_id>/comentar/', views.crear_comentario, name='crear_comentario'),
     path('album/<int:album_id>/comentario/<int:comentario_id>/editar/', views.actualizar_comentario, name='editar_comentario'),
     path('album/<int:album_id>/comentarios/buscar/',  views.busqueda_avanzada_comentarios,  name='busqueda_avanzada_comentarios'),
     path('album/<int:album_id>/comentario/<int:comentario_id>/eliminar/', views.eliminar_comentario, name='eliminar_comentario'),
     path('perfil/<str:nombre_usuario>/album/crear/', views.crear_album_con_canciones, name='crear_album'),
     path('cancion/editar/<int:cancion_id>/', views.editar_cancion, name='editar_cancion'),
     path('cancion/eliminar/<int:cancion_id>/', views.eliminar_cancion, name='eliminar_cancion'),
     path('album/<int:album_id>/agregar-cancion/', views.agregar_cancion_album, name='agregar_cancion_album'),
     path('busqueda/canciones/', views.busqueda_avanzada_canciones, name='busqueda_avanzada_canciones'),
     path('playlist/crear/', views.crear_playlist, name='crear_playlist'),
     path('playlists/<int:playlist_id>/editar/', views.editar_playlist, name='editar_playlist'),
     path('playlists/<int:playlist_id>/agregar-cancion/', views.agregar_cancion_playlist, name='agregar_cancion_playlist'),
     path('playlists/busqueda-avanzada/', views.busqueda_avanzada_playlists, name='busqueda_avanzada_playlists'),
     path('playlist/eliminar/<int:playlist_id>/', views.eliminar_playlist, name='eliminar_playlist'),
     path('chat/<int:usuario_id>/', views.crear_mensaje_privado, name='chat'),
     path('mensaje/editar/<int:mensaje_id>/', views.editar_mensaje, name='editar_mensaje'),
     path('chats/', views.lista_chats, name='lista_chats'),
     path('mensaje/eliminar/<int:mensaje_id>/', views.eliminar_mensaje, name='eliminar_mensaje'),
     

     #password reset aquí
     path('password-reset/', 
            auth_views.PasswordResetView.as_view(
                template_name='password_reset.html',  
                success_url='/password-reset/done/'
            ), 
            name='password_reset'),
        
     path('password-reset/done/', 
            auth_views.PasswordResetDoneView.as_view(
                template_name='password_reset_done.html'  
            ), 
            name='password_reset_done'),
        
     path('password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html',
            form_class=CustomSetPasswordForm,  
            success_url='/password-reset-complete/'
        ), 
        name='password_reset_confirm'),
        
     path('password-reset-complete/', 
            auth_views.PasswordResetCompleteView.as_view(
                template_name='password_reset_complete.html' 
            ), 
            name='password_reset_complete'),
    

     path('usuarios/<str:nombre_usuario>/seguidores/', views.lista_seguidores, name='usuarios_seguidores'),
     path('usuarios/<str:nombre_usuario>/seguidos/', views.lista_seguidos, name='usuarios_seguidos'),
     path('', views.index, name='index'),  # Página de inicio con enlaces a todas las URLs
     path('mensajes_privados/<int:emisor_id>/<int:receptor_id>/', views.mensajes_privados, name='mensajes_privados'),
     re_path(r'^perfil_usuario/(?P<nombre_usuario>[a-zA-Z0-9_]+)/$', views.perfil_usuario, name='perfil_usuario'),
     path('usuario/feed/', views.feed, name='feed'),
     path('cancion/<int:cancion_id>/detalles_cancion/', views.detalle_cancion, name='detalle_cancion'),
     path('album/<int:album_id>/detalles_album/', views.detalle_album, name='detalle_album'),
     path('album/<int:album_id>/canciones/', views.canciones_album, name='canciones_album'),
     path('canciones_guardadas/<str:nombre_usuario>/', views.canciones_guardadas, name="canciones_guardadas"),
     path('lista_albumes/<str:nombre_usuario>/', views.lista_albumes, name='lista_albumes'),
     path('album/<int:album_id>/comentarios/', views.comentarios_album, name='comentarios_album'),
     path('usuario/<str:nombre_usuario>/playlists/', views.lista_playlist, name='lista_playlist'),
     path('playlist/<int:playlist_id>/canciones/', views.canciones_playlist, name='canciones_playlist'),
     path('usuario/<str:nombre_usuario>/usuarios-que-no-sigue/', views.lista_no_sigue, name='lista_no_sigue'),
]
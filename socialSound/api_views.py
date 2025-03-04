from .models import *
from .serializer import *
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from .forms import *
from django.db.models import Count, Prefetch
from .forms import BusquedaUsuarioForm
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import Group



def manejar_error_api(error, operacion):

    if isinstance(error, serializers.ValidationError):
        print(f"Error de validación en {operacion}: {error.detail}")
        return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
    elif isinstance(error, ObjectDoesNotExist):
        print(f"Error 404 en {operacion}: {str(error)}")
        return Response(
            {"error": str(error)},
            status=status.HTTP_404_NOT_FOUND
        )
    else:
        print(f"Error 500 en {operacion}: {repr(error)}")
        return Response(
            {"error": "Error interno del servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lista_playlists(request):
    # Verificamos si el usuario tiene permiso para ver playlists
    if not request.user.has_perm('socialSound.view_playlist'):
        return Response(
            {"error": "No tienes permiso para ver playlists"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        playlists = Playlist.objects.select_related(
            'usuario'
        ).prefetch_related(
            Prefetch(
                'cancionplaylist_set',
                queryset=CancionPlaylist.objects.select_related('cancion')
            )
        ).annotate(
            total_canciones=Count('canciones', distinct=True)
        ).order_by('-fecha_creacion')
        
        serializer = PlaylistSerializerMejorado(playlists, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lista_albumes_usuario(request, nombre_usuario):
    # Verificamos si el usuario tiene permiso para ver álbumes
    if not request.user.has_perm('socialSound.view_album'):
        return Response(
            {"error": "No tienes permiso para ver álbumes"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        usuario = Usuario.objects.get(nombre_usuario=nombre_usuario)
        albumes = Album.objects.filter(usuario=usuario)\
                              .order_by('fecha_subida')\
                              .select_related('usuario')\
                              .prefetch_related('canciones')
       
        serializer = AlbumSerializerMejorado(albumes, many=True, context={'request': request}) 
        return Response(serializer.data)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=404,)
    except Exception as e:
        return Response({'error': str(e)}, status=500)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lista_albumes(request):
    # Verificamos si el usuario tiene permiso para ver álbumes
    if not request.user.has_perm('socialSound.view_album'):
        return Response(
            {"error": "No tienes permiso para ver álbumes"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        albumes = Album.objects.all()\
                               .order_by('fecha_subida')\
                               .select_related('usuario', 'detalle_album', 'estadisticasalbum')\
                               .prefetch_related('canciones', 'canciones__detalles')
        
        serializer = AlbumSerializerMejorado(albumes, many=True, context={'request': request})
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lista_usuarios_completa(request):
    print(f'{request.user}')
    # Verificamos si el usuario tiene permiso para ver usuarios
    if not request.user.has_perm('socialSound.view_usuario'):
        return Response(
            {"error": "No tienes permiso para ver usuarios"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        usuarios = Usuario.objects.prefetch_related(
            'siguiendo',
            'siguiendo__seguidor',
            'seguidores',
            'seguidores__seguido',
            'cliente',
            'moderador'
        ).annotate(
            seguidores_count=Count('siguiendo', distinct=True),
            seguidos_count=Count('seguidores', distinct=True)
        ).order_by('-date_joined')
        
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        print(f"Error en API: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=500
        )
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lista_canciones_completa(request):
    # Verificamos si el usuario tiene permiso para ver canciones
    if not request.user.has_perm('socialSound.view_cancion'):
        return Response(
            {"error": "No tienes permiso para ver canciones"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        canciones = Cancion.objects.select_related(
            'detalles',
            'usuario',
            'album'
        ).prefetch_related('likes',).order_by('-fecha_subida')
        
        serializer = CancionSerializerMejorado(canciones, many=True, context={'request': request})
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def canciones_por_genero(request):
    # Verificamos si el usuario tiene permiso para ver canciones
    if not request.user.has_perm('socialSound.view_cancion'):
        return Response(
            {"error": "No tienes permiso para ver canciones"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        canciones = Cancion.objects.select_related(
            'detalles',
            'usuario',
        ).prefetch_related(
            'likes'
        ).order_by('etiqueta')

        serializer = CancionSerializerMejorado(canciones, many=True, context={'request': request})
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usuario_buscar(request):
    # Verificamos si el usuario tiene permiso para ver usuarios
    if not request.user.has_perm('socialSound.view_usuario'):
        return Response(
            {"error": "No tienes permiso para ver usuarios"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    form = BusquedaUsuarioForm(request.query_params)
    if form.is_valid():
        texto = form.cleaned_data.get('textoBusqueda')
        usuarios = Usuario.objects.prefetch_related(
                'siguiendo',
                'siguiendo__seguidor',
                'seguidores',
                'seguidores__seguido',
                'cliente',
                'moderador',
                'albumes'
            ).annotate(
                seguidores_count=Count('siguiendo', distinct=True),
                seguidos_count=Count('seguidores', distinct=True),
                publicaciones_count=Count('albumes')
            ).order_by('-date_joined')

        if texto:
                usuarios = usuarios.filter(nombre_usuario__icontains=texto)
              
        serializer = UsuarioSerializer(usuarios, many=True)
        print(f'{serializer.data}')
        return Response(serializer.data)

    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usuario_busqueda_avanzada(request):
    # Verificamos si el usuario tiene permiso para ver usuarios
    if not request.user.has_perm('socialSound.view_usuario'):
        return Response(
            {"error": "No tienes permiso para ver usuarios"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if len(request.GET) > 0:
        formulario = BusquedaAvanzadaUsuarioForm_noValidaciones(request.query_params)
        if formulario.is_valid():
            usuarios = Usuario.objects.prefetch_related(
                'siguiendo',
                'siguiendo__seguidor',
                'seguidores',
                'seguidores__seguido',
                'cliente',
                'moderador', 
                'albumes'
            ).annotate(
                seguidores_count=Count('siguiendo', distinct=True),
                seguidos_count=Count('seguidores', distinct=True),
                publicaciones_count=Count('albumes', distinct=True)
            ).order_by('-date_joined')
        
                        
            nombre_usuario = formulario.cleaned_data.get('nombre_usuario')
            ciudad = formulario.cleaned_data.get('ciudad')
            edad_min = formulario.cleaned_data.get('edad_min')
            edad_max = formulario.cleaned_data.get('edad_max')
            bio_contains = formulario.cleaned_data.get('bio_contains')

            if nombre_usuario:
                usuarios = usuarios.filter(nombre_usuario__icontains=nombre_usuario)
            
            if ciudad:
                usuarios = usuarios.filter(ciudad__icontains=ciudad)
            
            if edad_min:
                fecha_max = date.today().replace(year=date.today().year - edad_min)
                usuarios = usuarios.filter(fecha_nac__lte=fecha_max)
            
            if edad_max:
                fecha_min = date.today().replace(year=date.today().year - edad_max)
                usuarios = usuarios.filter(fecha_nac__gte=fecha_min)
            
            if bio_contains:
                usuarios = usuarios.filter(bio__icontains=bio_contains)

            serializer = UsuarioSerializer(usuarios, many=True)
            return Response(serializer.data)
            
        return Response(formulario.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        formulario = BusquedaAvanzadaUsuarioForm(None)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def album_busqueda_avanzada(request):
    # Verificamos si el usuario tiene permiso para ver álbumes
    if not request.user.has_perm('socialSound.view_album'):
        return Response(
            {"error": "No tienes permiso para ver álbumes"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if len(request.GET) > 0:
        formulario = BusquedaAvanzadaAlbumForm(request.query_params)
        if formulario.is_valid():
            albumes = Album.objects.select_related('usuario').prefetch_related(
                'canciones',
                'reposts',
                'comentario_set'
            ).annotate(
                num_canciones=Count('canciones', distinct=True),
                num_comentarios=Count('comentario', distinct=True)
            )
            
            titulo = formulario.cleaned_data.get('titulo')
            artista = formulario.cleaned_data.get('artista')
            fecha_desde = formulario.cleaned_data.get('fecha_desde')
            fecha_hasta = formulario.cleaned_data.get('fecha_hasta')

            if titulo:
                albumes = albumes.filter(titulo__icontains=titulo)
            if artista:
                albumes = albumes.filter(artista__icontains=artista)
            if fecha_desde:
                albumes = albumes.filter(fecha_subida__gte=fecha_desde)
            if fecha_hasta:
                albumes = albumes.filter(fecha_subida__lte=fecha_hasta)

            serializer = AlbumSerializerMejorado(albumes, many=True)
            return Response(serializer.data)
            
        return Response(formulario.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cancion_busqueda_avanzada(request):
    # Verificamos si el usuario tiene permiso para ver canciones
    if not request.user.has_perm('socialSound.view_cancion'):
        return Response(
            {"error": "No tienes permiso para ver canciones"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if len(request.GET) > 0:
        formulario = BusquedaAvanzadaCancionForm(request.query_params)
        if formulario.is_valid():
            canciones = Cancion.objects.select_related(
                'usuario',
                'album',
                'detalles'
            ).prefetch_related('likes')
            
            titulo = formulario.cleaned_data.get('titulo')
            artista = formulario.cleaned_data.get('artista')
            etiqueta = formulario.cleaned_data.get('etiqueta')
            fecha_desde = formulario.cleaned_data.get('fecha_desde')
            fecha_hasta = formulario.cleaned_data.get('fecha_hasta')
            album = formulario.cleaned_data.get('album')

            if titulo:
                canciones = canciones.filter(titulo__icontains=titulo)
            if artista:
                canciones = canciones.filter(artista__icontains=artista)
            if etiqueta:
                canciones = canciones.filter(etiqueta=etiqueta)
            if fecha_desde:
                canciones = canciones.filter(fecha_subida__gte=fecha_desde)
            if fecha_hasta:
                canciones = canciones.filter(fecha_subida__lte=fecha_hasta)
            if album:
                canciones = canciones.filter(album__titulo__icontains=album)

            serializer = CancionSerializerMejorado(canciones, many=True)
            return Response(serializer.data)
            
        return Response(formulario.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def playlist_busqueda_avanzada(request):
    # Verificamos si el usuario tiene permiso para ver playlists
    if not request.user.has_perm('socialSound.view_playlist'):
        return Response(
            {"error": "No tienes permiso para ver playlists"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if len(request.GET) > 0:
        formulario = BusquedaAvanzadaPlaylistForm(request.query_params)
        if formulario.is_valid():
            # Obtener playlists según permisos
            if request.user.has_perm('socialSound.view_any_playlist'):
                playlists = Playlist.objects.select_related('usuario').prefetch_related(
                    'canciones',
                    'cancionplaylist_set',
                    'cancionplaylist_set__cancion'
                )
            else:
                playlists = Playlist.objects.select_related('usuario').prefetch_related(
                    'canciones',
                    'cancionplaylist_set',
                    'cancionplaylist_set__cancion'
                ).filter(
                    Q(publica=True) | Q(usuario=request.user)
                )
            
            nombre = formulario.cleaned_data.get('nombre')
            usuario = formulario.cleaned_data.get('usuario')
            fecha_desde = formulario.cleaned_data.get('fecha_desde')
            fecha_hasta = formulario.cleaned_data.get('fecha_hasta')
            publica = formulario.cleaned_data.get('publica')

            if nombre:
                playlists = playlists.filter(nombre__icontains=nombre)
            if usuario:
                playlists = playlists.filter(usuario__nombre_usuario__icontains=usuario)
            if fecha_desde:
                playlists = playlists.filter(fecha_creacion__gte=fecha_desde)
            if fecha_hasta:
                playlists = playlists.filter(fecha_creacion__lte=fecha_hasta)
            if publica:
                playlists = playlists.filter(publica=publica == 'True')

            serializer = PlaylistSerializerMejorado(playlists, many=True)
            return Response(serializer.data)
            
        return Response(formulario.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # Permitir registro sin autenticación
def usuario_create(request): 
    print(f"Iniciando creación de usuario con datos: {request.data}")
    usuarioCreateSerializer = UsuarioSerializerCreate(data=request.data)
    
    try:
        if usuarioCreateSerializer.is_valid():
            usuarioCreateSerializer.save()
            print("Usuario creado exitosamente")
            return Response("Usuario CREADO")
        else:
            print(f"Errores de validación: {usuarioCreateSerializer.errors}")
            return Response(
                usuarioCreateSerializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as error:
        return manejar_error_api(error, "crear_usuario")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usuario_detail(request, id):
    # Verificamos si el usuario tiene permiso para ver usuarios
    if not request.user.has_perm('socialSound.view_usuario'):
        return Response(
            {"error": "No tienes permiso para ver usuarios"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print(f"Obteniendo detalles del usuario {id}")
    try:
        usuario = Usuario.objects.get(id=id)
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)
    except Usuario.DoesNotExist as error:
        print(f"Usuario {id} no encontrado")
        return Response(
            {"error": "Usuario no encontrado"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return manejar_error_api(error, f"obtener_usuario_{id}")


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def usuario_update(request, id): 
    # Verificamos si el usuario tiene permiso para editar usuarios
    if not request.user.has_perm('socialSound.change_usuario'):
        return Response(
            {"error": "No tienes permiso para editar usuarios"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print(f"Actualizando usuario {id} con datos: {request.data}")
    try:
        usuario = Usuario.objects.get(id=id)
        
        # Verificamos si el usuario es el propietario o es moderador
        if usuario.id != request.user.id and not request.user.has_perm('socialSound.change_any_usuario'):
            return Response(
                {"error": "Solo puedes editar tu propio perfil"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        usuarioSerializer = UsuarioSerializerUpdate(
            instance=usuario,
            data=request.data
        )
        
        if usuarioSerializer.is_valid():
            usuarioSerializer.save()
            print(f"Usuario {id} actualizado correctamente")
            return Response("Usuario ACTUALIZADO")
        else:
            print(f"Errores de validación: {usuarioSerializer.errors}")
            return Response(
                usuarioSerializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
    except Usuario.DoesNotExist:
        print(f"Usuario {id} no encontrado")
        return Response(
            {"error": "Usuario no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return manejar_error_api(error, f"actualizar_usuario_{id}")
    
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def usuario_actualizar_nombre(request, usuario_id):
    # Verificamos si el usuario tiene permiso para editar usuarios
    if not request.user.has_perm('socialSound.change_usuario'):
        return Response(
            {"error": "No tienes permiso para editar usuarios"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print(f"Actualizando nombre de usuario {usuario_id} con datos: {request.data}")
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        
        # Verificamos si el usuario es el propietario o es moderador
        if usuario.id != request.user.id and not request.user.has_perm('socialSound.change_any_usuario'):
            return Response(
                {"error": "Solo puedes editar tu propio perfil"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UsuarioSerializerActualizarNombre(
            instance=usuario, 
            data=request.data
        )
        
        if serializer.is_valid():
            serializer.save()
            print(f"Nombre de usuario {usuario_id} actualizado correctamente")
            return Response("Usuario EDITADO")
        else:
            print(f"Errores de validación: {serializer.errors}")
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except Usuario.DoesNotExist:
        print(f"Usuario {usuario_id} no encontrado")
        return Response(
            {"error": "Usuario no encontrado"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return manejar_error_api(error, f"actualizar_nombre_usuario_{usuario_id}")


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def usuario_eliminar(request, usuario_id):
    # Verificamos si el usuario tiene permiso para eliminar usuarios
    if not request.user.has_perm('socialSound.delete_usuario'):
        return Response(
            {"error": "No tienes permiso para eliminar usuarios"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print(f"Eliminando usuario {usuario_id}")
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        
        # Verificamos si el usuario es el propietario o es moderador
        if usuario.id != request.user.id and not request.user.has_perm('socialSound.delete_any_usuario'):
            return Response(
                {"error": "Solo puedes eliminar tu propio perfil"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        usuario.delete()
        print(f"Usuario {usuario_id} eliminado correctamente")
        return Response("Usuario ELIMINADO")
    except Usuario.DoesNotExist:
        print(f"Usuario {usuario_id} no encontrado")
        return Response(
            {"error": "Usuario no encontrado"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return manejar_error_api(error, f"eliminar_usuario_{usuario_id}")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def album_list(request):
    # Verificamos si el usuario tiene permiso para ver álbumes
    if not request.user.has_perm('socialSound.view_album'):
        return Response(
            {"error": "No tienes permiso para ver álbumes"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print("Obteniendo lista de álbumes")
    try:
        albumes = Album.objects.all()
        serializer = AlbumSerializer(albumes, many=True)
        print("Lista de álbumes obtenida correctamente")
        return Response(serializer.data)
    except Exception as error:
        return manejar_error_api(error, "listar_albumes")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usuario_list(request):
    # Verificamos si el usuario tiene permiso para ver usuarios
    if not request.user.has_perm('socialSound.view_usuario'):
        return Response(
            {"error": "No tienes permiso para ver usuarios"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print("Obteniendo lista de usuarios")
    try:
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        print("Lista de usuarios obtenida correctamente")
        return Response(serializer.data)
    except Exception as error:
        return manejar_error_api(error, "listar_usuarios")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def album_crear(request):
    # Verificamos si el usuario tiene permiso para crear álbumes
    if not request.user.has_perm('socialSound.add_album'):
        return Response(
            {"error": "No tienes permiso para crear álbumes"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print(f"Creando álbum con datos: {request.data}")
    serializer = AlbumSerializerCrear(data=request.data)
    
    try:
        if serializer.is_valid():
            # Asegurarse de que el álbum esté asociado al usuario correcto
            if 'usuario' in serializer.validated_data:
                usuario_id = serializer.validated_data['usuario'].id
                # Si no es moderador, solo puede crear álbumes para sí mismo
                if usuario_id != request.user.id and not request.user.has_perm('socialSound.add_any_album'):
                    return Response(
                        {"error": "Solo puedes crear álbumes para ti mismo"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            album = serializer.save()
            print(f"Álbum creado exitosamente con ID: {album.id}")
            return Response("Album CREADO", status=status.HTTP_201_CREATED)
        else:
            print(f"Errores de validación: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as error:
        return manejar_error_api(error, "crear_album")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def album_detail(request, id):
    # Verificamos si el usuario tiene permiso para ver álbumes
    if not request.user.has_perm('socialSound.view_album'):
        return Response(
            {"error": "No tienes permiso para ver álbumes"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print(f"Obteniendo detalles del álbum {id}")
    try:
        album = Album.objects.get(id=id)
        serializer = AlbumSerializerCrear(album)
        print(f"Detalles del álbum {id} obtenidos correctamente")
        return Response(serializer.data)
    except Album.DoesNotExist:
        print(f"Álbum {id} no encontrado")
        return Response(
            {"error": "Album no encontrado"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return manejar_error_api(error, f"detalle_album_{id}")


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def album_update(request, id):
    # Verificamos si el usuario tiene permiso para editar álbumes
    if not request.user.has_perm('socialSound.change_album'):
        return Response(
            {"error": "No tienes permiso para editar álbumes"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print(f"Actualizando álbum {id} con datos: {request.data}")
    try:
        album = Album.objects.get(id=id)
        
        # Verificamos si el usuario es el propietario o es moderador
        if album.usuario.id != request.user.id and not request.user.has_perm('socialSound.change_any_album'):
            return Response(
                {"error": "Solo puedes editar tus propios álbumes"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AlbumSerializerCrear(album, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            print(f"Álbum {id} actualizado correctamente")
            return Response("Album ACTUALIZADO")
        else:
            print(f"Errores de validación: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Album.DoesNotExist:
        print(f"Álbum {id} no encontrado")
        return Response(
            {"error": "Album no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return manejar_error_api(error, f"actualizar_album_{id}")



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def album_delete(request, id):
    # Verificamos si el usuario tiene permiso para eliminar álbumes
    if not request.user.has_perm('socialSound.delete_album'):
        return Response(
            {"error": "No tienes permiso para eliminar álbumes"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print(f"Eliminando álbum {id}")
    try:
        album = Album.objects.get(id=id)
        
        # Verificamos si el usuario es el propietario o es moderador
        if album.usuario.id != request.user.id and not request.user.has_perm('socialSound.delete_any_album'):
            return Response(
                {"error": "Solo puedes eliminar tus propios álbumes"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        album.delete()
        print(f"Álbum {id} eliminado correctamente")
        return Response("Album eliminado correctamente")
    except Album.DoesNotExist:
        print(f"Álbum {id} no encontrado")
        return Response(
            {"error": "Album no encontrado"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return manejar_error_api(error, f"eliminar_album_{id}")


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def album_patch_titulo(request, id): 
    # Verificamos si el usuario tiene permiso para editar álbumes
    if not request.user.has_perm('socialSound.change_album'):
        return Response(
            {"error": "No tienes permiso para editar álbumes"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print(f"Actualizando título del álbum {id} con datos: {request.data}")
    try:
        album = Album.objects.get(id=id)
        
        # Verificamos si el usuario es el propietario o es moderador
        if album.usuario.id != request.user.id and not request.user.has_perm('socialSound.change_any_album'):
            return Response(
                {"error": "Solo puedes editar tus propios álbumes"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AlbumSerializerTitulo(
            album,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            print(f"Título del álbum {id} actualizado correctamente")
            return Response("Título del álbum ACTUALIZADO")
        else:
            print(f"Errores de validación: {serializer.errors}")
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
    except Album.DoesNotExist:
        print(f"Álbum {id} no encontrado")
        return Response(
            {"error": "Álbum no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return manejar_error_api(error, f"actualizar_titulo_album_{id}")


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def playlist_delete(request, id):
    # Verificamos si el usuario tiene permiso para eliminar playlists
    if not request.user.has_perm('socialSound.delete_playlist'):
        return Response(
            {"error": "No tienes permiso para eliminar playlists"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print(f"Eliminando playlist {id}")
    try:
        playlist = Playlist.objects.get(id=id)
        
        # Verificamos si el usuario es el propietario o es moderador
        if playlist.usuario.id != request.user.id and not request.user.has_perm('socialSound.delete_any_playlist'):
            return Response(
                {"error": "Solo puedes eliminar tus propias playlists"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        playlist.delete()
        print(f"Playlist {id} eliminada correctamente")
        return Response("Playlist eliminada correctamente")
    except Playlist.DoesNotExist:
        print(f"Playlist {id} no encontrada")
        return Response(
            {"error": "Playlist no encontrada"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return manejar_error_api(error, f"eliminar_playlist_{id}")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def playlist_create(request):
    # Verificamos si el usuario tiene permiso para crear playlists
    if not request.user.has_perm('socialSound.add_playlist'):
        return Response(
            {"error": "No tienes permiso para crear playlists"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print(f"Creando playlist con datos: {request.data}")
    serializer = PlaylistSerializerCreate(data=request.data)
    
    try:
        if serializer.is_valid():
            # Asegurarse de que la playlist esté asociada al usuario correcto
            if 'usuario' in serializer.validated_data:
                usuario_id = serializer.validated_data['usuario'].id
                # Si no es moderador, solo puede crear playlists para sí mismo
                if usuario_id != request.user.id and not request.user.has_perm('socialSound.add_any_playlist'):
                    return Response(
                        {"error": "Solo puedes crear playlists para ti mismo"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            serializer.save()
            print("Playlist creada exitosamente")
            return Response("Playlist CREADA")
        else:
            print(f"Errores de validación: {serializer.errors}")
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as error:
        return manejar_error_api(error, "crear_playlist")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_canciones(request):
    # Verificamos si el usuario tiene permiso para ver canciones
    if not request.user.has_perm('socialSound.view_cancion'):
        return Response(
            {"error": "No tienes permiso para ver canciones"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print("Obteniendo lista de canciones")
    try:
        canciones = Cancion.objects.all()
        serializer = CancionSerializerMejorado(canciones, many=True)
        print("Lista de canciones obtenida correctamente")
        return Response(serializer.data)
    except Exception as error:
        return manejar_error_api(error, "listar_canciones")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def playlist_detail(request, id):
    # Verificamos si el usuario tiene permiso para ver playlists
    if not request.user.has_perm('socialSound.view_playlist'):
        return Response(
            {"error": "No tienes permiso para ver playlists"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print(f"Obteniendo detalles de playlist {id}")
    try:
        playlist = Playlist.objects.get(id=id)
        
        # Si la playlist es privada, Verificamos que el usuario sea el propietario o moderador
        if not playlist.publica and playlist.usuario.id != request.user.id and not request.user.has_perm('socialSound.view_any_playlist'):
            return Response(
                {"error": "No tienes permiso para ver esta playlist privada"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PlaylistSerializerMejorado(playlist)
        print(f"Detalles de playlist {id} obtenidos correctamente")
        return Response(serializer.data)
    except Playlist.DoesNotExist:
        print(f"Playlist {id} no encontrada")
        return Response(
            {"error": "Playlist no encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return manejar_error_api(error, f"detalle_playlist_{id}")


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def playlist_update(request, id):
    # Verificamos si el usuario tiene permiso para editar playlists
    if not request.user.has_perm('socialSound.change_playlist'):
        return Response(
            {"error": "No tienes permiso para editar playlists"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print(f"Actualizando playlist {id} con datos: {request.data}")
    try:
        playlist = Playlist.objects.get(id=id)
        
        # Verificamos si el usuario es el propietario o es moderador
        if playlist.usuario.id != request.user.id and not request.user.has_perm('socialSound.change_any_playlist'):
            return Response(
                {"error": "Solo puedes editar tus propias playlists"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data.copy()
        data.pop("usuario", None) 

        serializer = PlaylistSerializerUpdate(playlist, data=data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            print(f"Playlist {id} actualizada correctamente")
            return Response({"message": "Playlist actualizada correctamente"})
        else:
            print(f"Errores de validación: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Playlist.DoesNotExist:
        print(f"Playlist {id} no encontrada")
        return Response(
            {"error": "Playlist no encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return manejar_error_api(error, f"actualizar_playlist_{id}")

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def playlist_patch_canciones(request, id):
    # Verificamos si el usuario tiene permiso para editar playlists
    if not request.user.has_perm('socialSound.change_playlist'):
        return Response(
            {"error": "No tienes permiso para editar playlists"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print(f"Actualizando canciones de playlist {id} con datos: {request.data}")
    try:
        playlist = Playlist.objects.get(id=id)
        
        # Verificamos si el usuario es el propietario o es moderador
        if playlist.usuario.id != request.user.id and not request.user.has_perm('socialSound.change_any_playlist'):
            return Response(
                {"error": "Solo puedes editar tus propias playlists"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PlaylistSerializerCanciones(playlist, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            print(f"Canciones de playlist {id} actualizadas correctamente")
            return Response("Canciones de la playlist actualizadas")
        else:
            print(f"Errores de validación: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Playlist.DoesNotExist:
        print(f"Playlist {id} no encontrada")
        return Response(
            {"error": "Playlist no encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return manejar_error_api(error, f"actualizar_canciones_playlist_{id}")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_create(request):
    # Verificamos si el usuario tiene permiso para crear likes
    if not request.user.has_perm('socialSound.add_like'):
        return Response(
            {"error": "No tienes permiso para dar like a canciones"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print(f"Creando like con datos: {request.data}")
    serializer = LikeSerializerCreate(data=request.data)
    
    try:
        if serializer.is_valid():
            # Asegurarse de que el like esté asociado al usuario correcto
            if 'usuario' in serializer.validated_data:
                usuario_id = serializer.validated_data['usuario'].id
                # Si no es moderador, solo puede dar like usando su propio usuario
                if usuario_id != request.user.id and not request.user.has_perm('socialSound.add_any_like'):
                    return Response(
                        {"error": "Solo puedes dar like usando tu propio usuario"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            serializer.save()
            print("Like creado exitosamente")
            return Response("Like creado")
        else:
            print(f"Errores de validación: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as error:
        return manejar_error_api(error, "crear_like")


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def like_delete(request):
    # Verificamos si el usuario tiene permiso para eliminar likes
    if not request.user.has_perm('socialSound.delete_like'):
        return Response(
            {"error": "No tienes permiso para quitar likes"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print(f"Eliminando like con datos: {request.data}")
    try:
        like = Like.objects.get(
            usuario_id=request.data['usuario'],
            cancion_id=request.data['cancion']
        )
        
        # Verificamos si el usuario es el propietario o es moderador
        if like.usuario.id != request.user.id and not request.user.has_perm('socialSound.delete_any_like'):
            return Response(
                {"error": "Solo puedes quitar tus propios likes"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        like.delete()
        print("Like eliminado correctamente")
        return Response("Like eliminado correctamente")
    except Like.DoesNotExist:
        print("Like no encontrado para la combinación usuario-canción")
        return Response(
            {"error": "No existe like para esta combinación de usuario y canción"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return manejar_error_api(error, "eliminar_like")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancion_playlist_create(request):
    # Verificamos si el usuario tiene permiso para añadir canciones a playlists
    if not request.user.has_perm('socialSound.add_cancion_playlist'):
        return Response(
            {"error": "No tienes permiso para añadir canciones a playlists"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    print("Datos recibidos:", request.data)
    # Convertir IDs de string a int
    data = request.data.copy()
    data['canciones'] = [int(id) for id in request.data.get('canciones', [])]
    
    try:
        # Verificamos que el usuario sea el propietario de la playlist o moderador
        playlist_id = int(data['playlist'])
        playlist = Playlist.objects.get(id=playlist_id)
        
        if playlist.usuario.id != request.user.id and not request.user.has_perm('socialSound.add_any_cancion_playlist'):
            return Response(
                {"error": "Solo puedes añadir canciones a tus propias playlists"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CancionPlaylistSerializerMejorado(data=data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response("Canciones añadidas a playlist")
            except serializers.ValidationError as error:
                return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
            except Exception as error:
                print(repr(error))
                return Response(repr(error), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Playlist.DoesNotExist:
        return Response(
            {"error": "Playlist no encontrada"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return manejar_error_api(error, "crear_cancion_playlist")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def detalle_album_create(request, album_id):
    # Verificamos si el usuario tiene permiso para añadir detalles a álbumes
    if not request.user.has_perm('socialSound.add_detalle_album'):
        return Response(
            {"error": "No tienes permiso para añadir detalles a álbumes"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Verificamos que el usuario sea el propietario del álbum o moderador
        album = Album.objects.get(id=album_id)
        
        if album.usuario.id != request.user.id and not request.user.has_perm('socialSound.add_any_detalle_album'):
            return Response(
                {"error": "Solo puedes añadir detalles a tus propios álbumes"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data.copy()
        data['album'] = album_id

        serializer = DetalleAlbumSerializerCreate(data=data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response("Detalle de álbum CREADO")
            except serializers.ValidationError as error:
                return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
            except Exception as error:
                print(repr(error))
                return Response(repr(error), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Album.DoesNotExist:
        return Response(
            {"error": "Álbum no encontrado"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return manejar_error_api(error, "crear_detalle_album")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalle_album_detail(request, id):
    # Verificamos si el usuario tiene permiso para ver detalles de álbumes
    if not request.user.has_perm('socialSound.view_detalle_album'):
        return Response(
            {"error": "No tienes permiso para ver detalles de álbumes"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        detalle = DetalleAlbum.objects.get(album_id=id)
        print("Detalle encontrado, serializando...")
        serializer = DetalleAlbumSerializer(detalle)
        return Response(serializer.data)
    except DetalleAlbum.DoesNotExist:
        return Response(
            {"error": "Detalle de álbum no encontrado"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return manejar_error_api(error, f"detalle_album_detail_{id}")


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def detalle_album_update(request, id):
    # Verificamos si el usuario tiene permiso para editar detalles de álbumes
    if not request.user.has_perm('socialSound.change_detalle_album'):
        return Response(
            {"error": "No tienes permiso para editar detalles de álbumes"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        detalle = DetalleAlbum.objects.get(id=id)
        
        # Verificamos si el usuario es el propietario del álbum o es moderador
        if detalle.album.usuario.id != request.user.id and not request.user.has_perm('socialSound.change_any_detalle_album'):
            return Response(
                {"error": "Solo puedes editar detalles de tus propios álbumes"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DetalleAlbumSerializerCreate(detalle, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("Detalle de álbum ACTUALIZADO")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except DetalleAlbum.DoesNotExist:
        return Response(
            {"error": "Detalle de álbum no encontrado"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as error:
        return manejar_error_api(error, f"actualizar_detalle_album_{id}")



from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializerCreate

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                return Response("Usuario CREADO")
            except Exception as error:
                return Response(str(error), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                self.perform_update(serializer)
                return Response("Usuario ACTUALIZADO")
            except Exception as error:
                return Response(str(error), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response("Usuario ELIMINADO")
        except Exception as error:
            return Response(str(error), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def actualizar_nombre(self, request, pk=None):
        usuario = self.get_object()
        serializer = self.get_serializer(usuario, data=request.data, partial=True)
        
        try:
          
            nuevo_nombre = request.data.get('nombre_usuario')
            if nuevo_nombre and Usuario.objects.filter(nombre_usuario=nuevo_nombre).exclude(id=usuario.id).exists():
                return Response(
                    {'nombre_usuario': 'Este nombre de usuario ya está en uso'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if serializer.is_valid():
                serializer.save()
                return Response("Nombre de usuario actualizado correctamente")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as error:
            return Response(str(error), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def validar_nombre(self, request):
        nombre = request.query_params.get('nombre_usuario', '')
        existe = Usuario.objects.filter(nombre_usuario=nombre).exists()
        if existe:
            return Response(
                {'mensaje': 'El nombre de usuario ya existe'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({'mensaje': 'Nombre de usuario disponible'})

    @action(detail=False, methods=['get'])
    def validar_email(self, request):
        email = request.query_params.get('email', '')
        existe = Usuario.objects.filter(email=email).exists()
        if existe:
            return Response(
                {'mensaje': 'El email ya está registrado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({'mensaje': 'Email disponible'})
    
class registrar_usuario(generics.CreateAPIView):
    serializer_class = UsuarioSerializerRegistro
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = UsuarioSerializerRegistro(data=request.data)
        if serializer.is_valid():
            try:
                rol = request.data.get("rol")
                
                # Crear el usuario
                user = Usuario.objects.create_user(
                    nombre_usuario=serializer.data.get("username"),
                    email=serializer.data.get("email"),
                    password=serializer.data.get("password1"),
                    rol=rol,
                )
                
                # Asignar rol y crear perfil correspondiente
                if int(rol) == Usuario.CLIENTE:
                    grupo = Group.objects.get_or_create(name='Clientes')[0]
                    grupo.user_set.add(user)
                    cliente = Cliente.objects.create(usuario=user)
                    cliente.save()
                    
                elif int(rol) == Usuario.MODERADOR:
                    grupo = Group.objects.get_or_create(name='Moderadores')[0]
                    grupo.user_set.add(user)
                    moderador = Moderador.objects.create(usuario=user)
                    moderador.save()
                
                # Serializar usuario para la respuesta
                usuario_serializado = UsuarioSerializer(user)
                return Response(usuario_serializado.data)
                
            except Exception as error:
                return Response({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from oauth2_provider.models import AccessToken     

@api_view(['GET'])
@permission_classes([AllowAny])  
def obtener_usuario_token(request, token):
    try:
        modelo_token = AccessToken.objects.get(token=token)
        usuario = Usuario.objects.get(id=modelo_token.user.id)
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)
    except AccessToken.DoesNotExist:
        return Response({"error": "Token no válido"}, status=400)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_cancion(request):
    # Verificar permisos
    if not request.user.has_perm('socialSound.add_like'):
        return Response(
            {"error": "No tienes permiso para dar like a canciones"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        serializer = LikeSessionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Obtener la canción validada por el serializer
            cancion = serializer.validated_data['cancion']
            
       
            Like.objects.create(
                usuario=request.user,
                cancion=cancion
            )
            
            return Response(
                {"message": "Like añadido correctamente"},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        return manejar_error_api(e, "like_cancion")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unlike_cancion(request):

    if not request.user.has_perm('socialSound.delete_like'):
        return Response(
            {"error": "No tienes permiso para quitar likes"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
      
        cancion_id = request.data.get('cancion')
        if not cancion_id:
            return Response(
                {"error": "Se requiere el ID de la canción"},
                status=status.HTTP_400_BAD_REQUEST
            )
      
        like = Like.objects.filter(
            usuario=request.user,
            cancion_id=cancion_id
        ).first()
        
        if not like:
            return Response(
                {"error": "No has dado like a esta canción"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        like.delete()
        
        return Response(
            {"message": "Like eliminado correctamente"},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return manejar_error_api(e, "unlike_cancion")
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def seguir_usuario_api(request):
    # Verificar permisos
    if not request.user.has_perm('socialSound.add_seguidores'):
        return Response(
            {"error": "No tienes permiso para seguir usuarios"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Obtener el id del usuario a seguir
        usuario_id = request.data.get('usuario_id')
        if not usuario_id:
            return Response(
                {"error": "Se requiere el ID del usuario a seguir"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que el usuario existe
        try:
            usuario_a_seguir = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que no se siga a uno mismo
        if request.user.id == usuario_a_seguir.id:
            return Response(
                {"error": "No puedes seguirte a ti mismo"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si ya se sigue al usuario
        ya_sigue = Seguidores.objects.filter(
            seguidor=request.user,
            seguido=usuario_a_seguir
        ).exists()
        
        if ya_sigue:
            return Response(
                {"message": "Ya sigues a este usuario", "is_following": True},
                status=status.HTTP_200_OK
            )
        
        # Crear la relación de seguidor
        Seguidores.objects.create(
            seguidor=request.user,
            seguido=usuario_a_seguir
        )
        
        return Response(
            {"message": "Ahora sigues a este usuario", "is_following": True},
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        return manejar_error_api(e, "seguir_usuario")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def dejar_seguir_usuario_api(request):

    if not request.user.has_perm('socialSound.delete_seguidores'):
        return Response(
            {"error": "No tienes permiso para dejar de seguir usuarios"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        usuario_id = request.data.get('usuario_id')
        if not usuario_id:
            return Response(
                {"error": "Se requiere el ID del usuario a dejar de seguir"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        seguidor = Seguidores.objects.filter(
            seguidor=request.user,
            seguido_id=usuario_id
        ).first()
        
        if not seguidor:
            return Response(
                {"error": "No sigues a este usuario", "is_following": False},
                status=status.HTTP_404_NOT_FOUND
            )
        
        seguidor.delete()
        
        return Response(
            {"message": "Has dejado de seguir a este usuario", "is_following": False},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return manejar_error_api(e, "dejar_seguir_usuario")

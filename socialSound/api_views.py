from .models import *
from .serializer import *
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .forms import *
from django.db.models import Count, Prefetch
from .forms import BusquedaUsuarioForm
from django.core.exceptions import ObjectDoesNotExist


@api_view(['GET'])
def lista_playlists(request):
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
def lista_albumes_usuario(request, nombre_usuario):
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
def lista_albumes(request):
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
def lista_usuarios_completa(request):
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
def lista_canciones_completa(request):
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
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def canciones_por_genero(request):
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



## BUSQUEDAS API

@api_view(['GET'])
def usuario_buscar(request):
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
def usuario_busqueda_avanzada(request):
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
def album_busqueda_avanzada(request):
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
def cancion_busqueda_avanzada(request):
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
def playlist_busqueda_avanzada(request):
    if len(request.GET) > 0:
        formulario = BusquedaAvanzadaPlaylistForm(request.query_params)
        if formulario.is_valid():
            playlists = Playlist.objects.select_related('usuario').prefetch_related(
                'canciones',
                'cancionplaylist_set',
                'cancionplaylist_set__cancion'
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

@api_view(['POST'])
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
def usuario_detail(request, id):
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
def usuario_update(request, id): 
    print(f"Actualizando usuario {id} con datos: {request.data}")
    try:
        usuario = Usuario.objects.get(id=id)
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
def usuario_actualizar_nombre(request, usuario_id):
    print(f"Actualizando nombre de usuario {usuario_id} con datos: {request.data}")
    try:
        usuario = Usuario.objects.get(id=usuario_id)
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
def usuario_eliminar(request, usuario_id):
    print(f"Eliminando usuario {usuario_id}")
    try:
        usuario = Usuario.objects.get(id=usuario_id)
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
def album_list(request):
    print("Obteniendo lista de álbumes")
    try:
        albumes = Album.objects.all()
        serializer = AlbumSerializer(albumes, many=True)
        print("Lista de álbumes obtenida correctamente")
        return Response(serializer.data)
    except Exception as error:
        return manejar_error_api(error, "listar_albumes")

@api_view(['GET'])
def usuario_list(request):
    print("Obteniendo lista de usuarios")
    try:
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        print("Lista de usuarios obtenida correctamente")
        return Response(serializer.data)
    except Exception as error:
        return manejar_error_api(error, "listar_usuarios")

@api_view(['POST'])
def album_crear(request):
    print(f"Creando álbum con datos: {request.data}")
    serializer = AlbumSerializerCrear(data=request.data)
    
    try:
        if serializer.is_valid():
            album = serializer.save()
            print(f"Álbum creado exitosamente con ID: {album.id}")
            return Response("Album CREADO", status=status.HTTP_201_CREATED)
        else:
            print(f"Errores de validación: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as error:
        return manejar_error_api(error, "crear_album")

@api_view(['GET'])
def album_detail(request, id):
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
def album_update(request, id):
    print(f"Actualizando álbum {id} con datos: {request.data}")
    try:
        album = Album.objects.get(id=id)
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
def album_delete(request, id):
    print(f"Eliminando álbum {id}")
    try:
        album = Album.objects.get(id=id)
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
def album_patch_titulo(request, id): 
    print(f"Actualizando título del álbum {id} con datos: {request.data}")
    try:
        album = Album.objects.get(id=id)
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
def playlist_delete(request, id):
    print(f"Eliminando playlist {id}")
    try:
        playlist = Playlist.objects.get(id=id)
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
def playlist_create(request):
    print(f"Creando playlist con datos: {request.data}")
    serializer = PlaylistSerializerCreate(data=request.data)
    
    try:
        if serializer.is_valid():
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
def obtener_canciones(request):
    print("Obteniendo lista de canciones")
    try:
        canciones = Cancion.objects.all()
        serializer = CancionSerializerMejorado(canciones, many=True)
        print("Lista de canciones obtenida correctamente")
        return Response(serializer.data)
    except Exception as error:
        return manejar_error_api(error, "listar_canciones")

@api_view(['GET'])
def playlist_detail(request, id):
    print(f"Obteniendo detalles de playlist {id}")
    try:
        playlist = Playlist.objects.get(id=id)
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
def playlist_update(request, id):
    print(f"Actualizando playlist {id} con datos: {request.data}")
    try:
        playlist = Playlist.objects.get(id=id)
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
def playlist_patch_canciones(request, id):
    print(f"Actualizando canciones de playlist {id} con datos: {request.data}")
    try:
        playlist = Playlist.objects.get(id=id)
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
def like_create(request):
    print(f"Creando like con datos: {request.data}")
    serializer = LikeSerializerCreate(data=request.data)
    
    try:
        if serializer.is_valid():
            serializer.save()
            print("Like creado exitosamente")
            return Response("Like creado")
        else:
            print(f"Errores de validación: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as error:
        return manejar_error_api(error, "crear_like")

@api_view(['DELETE'])
def like_delete(request):
    print(f"Eliminando like con datos: {request.data}")
    try:
        like = Like.objects.get(
            usuario_id=request.data['usuario'],
            cancion_id=request.data['cancion']
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
def cancion_playlist_create(request):
    print("Datos recibidos:", request.data)
    # Convertir IDs de string a int
    data = request.data.copy()
    data['canciones'] = [int(id) for id in request.data.get('canciones', [])]
    
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


@api_view(['POST'])
def detalle_album_create(request, album_id):

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



@api_view(['GET'])
def detalle_album_detail(request, id):
        detalle = DetalleAlbum.objects.get(album_id=id)
        print("Detalle encontrado, serializando...")
        serializer = DetalleAlbumSerializer(detalle)
        return Response(serializer.data)
  
     

@api_view(['PUT'])
def detalle_album_update(request, id):
    try:
        detalle = DetalleAlbum.objects.get(id=id)
    except DetalleAlbum.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = DetalleAlbumSerializerCreate(detalle, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response("Detalle de álbum ACTUALIZADO")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




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

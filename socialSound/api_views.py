from .models import *
from .serializer import *
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .forms import *
from django.db.models import Count, Prefetch, Q
from .forms import BusquedaUsuarioForm


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



@api_view(['POST'])
def usuario_create(request): 
    print(request.data)
    usuarioCreateSerializer = UsuarioSerializerCreate(data=request.data)
    if usuarioCreateSerializer.is_valid():
        try:
            usuarioCreateSerializer.save()
            return Response("Usuario CREADO")
        except serializers.ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print(repr(error))
            return Response(repr(error), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        print("Errores del serializer:", usuarioCreateSerializer.errors)
        return Response(usuarioCreateSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

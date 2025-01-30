from .models import *
from .serializer import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .forms import *
from django.db.models import Count, Prefetch


@api_view(['GET'])
def usuarios(request):
    try:
        usuarios = Usuario.objects.prefetch_related('albumes', 'albumes__canciones').all()
        serializer = UsuarioSerializer(usuarios, many=True)
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
       
        serializer = AlbumSerializerMejorado(albumes, many=True) 
        return Response(serializer.data)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=404)
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
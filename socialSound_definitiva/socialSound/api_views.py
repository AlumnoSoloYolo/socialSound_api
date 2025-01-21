from .models import *
from .serializer import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .forms import *
from django.db.models import Prefetch


@api_view(['GET'])
def usuarios(request):
    try:
        usuarios = Usuario.objects.prefetch_related('albumes', 'albumes__canciones').all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
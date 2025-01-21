from rest_framework import serializers
from .models import *



class SeguidoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seguidores
        fields = '__all__'


class DetalleAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleAlbum
        fields = '__all__'

class EstadisticasAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadisticasAlbum
        fields = '__all__'



class DetallesCancionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallesCancion
        fields = '__all__'

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = '__all__'

class CancionPlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancionPlaylist
        fields = '__all__'

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class ComentarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comentario
        fields = '__all__'

class MensajePrivadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MensajePrivado
        fields = '__all__'

class GuardadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardado
        fields = '__all__'
        



class CancionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cancion
        fields = '__all__'

class AlbumSerializer(serializers.ModelSerializer):
    canciones = CancionSerializer(many=True, read_only=True)  # many=True porque un álbum tiene múltiples canciones

    class Meta:
        model = Album
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    albumes = AlbumSerializer(many=True, read_only=True)  # many=True porque un usuario tiene múltiples álbumes

    class Meta:
        model = Usuario
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class ModeradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moderador
        fields = '__all__'



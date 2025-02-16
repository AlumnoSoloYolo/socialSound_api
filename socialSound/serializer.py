from rest_framework import serializers
from .models import *


class UsuarioBasicoSerializer(serializers.ModelSerializer):
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    date_joined = serializers.DateTimeField(format="%d-%m-%Y", read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'nombre_usuario', 'email', 'foto_perfil', 
            'ciudad', 'rol', 'rol_display', 'date_joined'
        ]

class SeguidoresSerializerMejorado(serializers.ModelSerializer):
    seguidor = UsuarioBasicoSerializer(read_only=True)
    seguido = UsuarioBasicoSerializer(read_only=True)
    fecha_inicio = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    
    class Meta:
        model = Seguidores
        fields = ['id', 'seguidor', 'seguido', 'fecha_inicio']

class ClienteSerializerMejorado(serializers.ModelSerializer):
    usuario = UsuarioBasicoSerializer(read_only=True)
    
    class Meta:
        model = Cliente
        fields = ['id', 'usuario', 'genero_favorito', 'artista_favorito', 
                 'acepta_terminos']

class ModeradorSerializerMejorado(serializers.ModelSerializer):
    usuario = UsuarioBasicoSerializer(read_only=True)
    
    class Meta:
        model = Moderador
        fields = ['id', 'usuario', 'experiencia_moderacion', 'area_especialidad', 
                 'codigo_moderador']

class UsuarioSerializer(serializers.ModelSerializer):
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    seguidores = SeguidoresSerializerMejorado(source='siguiendo', many=True, read_only=True)
    seguidos = SeguidoresSerializerMejorado(source='seguidores', many=True, read_only=True)
    cliente = ClienteSerializerMejorado(read_only=True)
    moderador = ModeradorSerializerMejorado(read_only=True)
    seguidores_count = serializers.IntegerField(read_only=True)
    seguidos_count = serializers.IntegerField(read_only=True)
    fecha_nac = serializers.DateField(format="%d-%m-%Y", read_only=True)
    # foto_perfil_url = serializers.SerializerMethodField()

    # def get_foto_perfil_url(self, obj):
    #     if obj.portada:
    #         request = self.context.get('request')
    #         if request:
    #             return request.build_absolute_uri(obj.foto_perfil.url)
    #     return None

    class Meta:
        model = Usuario
        fields = [
            'id', 'nombre_usuario', 'email', 'foto_perfil', 
            'ciudad', 'rol', 'rol_display', 'fecha_nac',
            'seguidores', 'seguidos', 'seguidores_count', 
            'seguidos_count', 'cliente', 'moderador', 'bio'
        ]



class DetallesCancionSerializer(serializers.ModelSerializer):
    duracion_formateada = serializers.SerializerMethodField()
    
    class Meta:
        model = DetallesCancion
        fields = ['letra', 'creditos', 'duracion', 'idioma', 'duracion_formateada']
    
    def get_duracion_formateada(self, obj):
        return obj.duracion_formateada

class DetalleAlbumSerializer(serializers.ModelSerializer):
    numero_comentarios = serializers.SerializerMethodField()
 
    
    class Meta:
        model = DetalleAlbum
        fields = ['productor', 'estudio_grabacion', 'numero_pistas', 
                 'sello_discografico', 'numero_comentarios']
    
    def get_numero_comentarios(self, obj):
        return obj.numero_comentarios

   

class EstadisticasAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadisticasAlbum
        fields = ['reproducciones', 'likes', 'comentarios']

class CancionSerializerMejorado(serializers.ModelSerializer):
    detalles = DetallesCancionSerializer(read_only=True)
    etiqueta_display = serializers.CharField(source='get_etiqueta_display', read_only=True)
    fecha_subida = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    usuario = UsuarioSerializer(read_only=True)
    likes = serializers.PrimaryKeyRelatedField(source='like_set.all', many=True, read_only=True)
    album_titulo = serializers.SerializerMethodField()
    portada_url = serializers.SerializerMethodField()
    archivo_audio_url = serializers.SerializerMethodField()

    
    def get_album_titulo(self, obj):
        return obj.album.titulo if obj.album else None
    
    def get_portada_url(self, obj):
        if obj.portada:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.portada.url)
        return None
    
    def get_archivo_audio_url(self, obj):
        if obj.archivo_audio:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.archivo_audio.url)
        return None
    
    class Meta:
        model = Cancion
        fields = [
            'id', 'titulo', 'artista', 'archivo_audio', 'archivo_audio_url', 'portada', 'portada_url',
            'fecha_subida', 'etiqueta', 'etiqueta_display', 'detalles',
            'usuario', 'likes', 'album_titulo'
        ]

class AlbumSerializerMejorado(serializers.ModelSerializer):
    canciones = CancionSerializerMejorado(many=True, read_only=True)
    detalle_album = DetalleAlbumSerializer(read_only=True)
    estadisticasalbum = EstadisticasAlbumSerializer(read_only=True)
    fecha_subida = serializers.DateField(format="%d-%m-%Y", read_only=True)
    usuario = UsuarioSerializer(read_only=True)
    # portada_url = serializers.SerializerMethodField()



    # def get_portada_url(self, obj):
    #     if obj.portada:
    #         request = self.context.get('request')
    #         if request:
    #             return request.build_absolute_uri(obj.portada.url)
    #     return None
    
    class Meta:
        model = Album
        fields = [
            'id', 'titulo', 'artista', 'usuario', 'fecha_subida', 
            'portada', 'descripcion', 'canciones', 'detalle_album', 
            'estadisticasalbum'
        ]

class ComentarioSerializerMejorado(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    fecha_publicacion = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    
    class Meta:
        model = Comentario
        fields = ['id', 'contenido', 'fecha_publicacion', 'album', 'usuario']

class LikeSerializerMejorado(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    fecha_like = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'usuario', 'cancion', 'fecha_like']

class CancionPlaylistSerializerMejorado(serializers.ModelSerializer):
    cancion = CancionSerializerMejorado(read_only=True)
    fecha_agregada = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    
    class Meta:
        model = CancionPlaylist
        fields = ['cancion', 'orden', 'fecha_agregada']

class PlaylistSerializerMejorado(serializers.ModelSerializer):
    canciones = CancionPlaylistSerializerMejorado(source='cancionplaylist_set', many=True, read_only=True)
    fecha_creacion = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    usuario = UsuarioSerializer(read_only=True)
    total_canciones = serializers.SerializerMethodField()
    
    class Meta:
        model = Playlist
        fields = ['id', 'nombre', 'descripcion', 'fecha_creacion', 
                 'usuario', 'canciones', 'publica', 'total_canciones']
    
    def get_total_canciones(self, obj):
        return obj.canciones.count()

class MensajePrivadoSerializerMejorado(serializers.ModelSerializer):
    emisor = UsuarioSerializer(read_only=True)
    receptor = UsuarioSerializer(read_only=True)
    fecha_envio = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    
    class Meta:
        model = MensajePrivado
        fields = ['id', 'emisor', 'receptor', 'contenido', 'fecha_envio', 'leido']


import base64
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

class UsuarioSerializerCreate(serializers.ModelSerializer):
    foto_perfil = serializers.CharField(required=False, allow_blank=True)  # Cambiado a CharField para recibir el base64
    
    class Meta:
        model = Usuario
        fields = ['nombre_usuario', 'email', 'password', 
                 'bio', 'foto_perfil']
    
    def create(self, validated_data):
        foto_base64 = validated_data.pop('foto_perfil', None)  # Extraemos la foto en base64

        print("Guardando foto:", foto_base64[:100] if foto_base64 else None)
        
        usuario = Usuario.objects.create_user(
            nombre_usuario=validated_data["nombre_usuario"],
            email=validated_data["email"],
            password=validated_data["password"],
            bio=validated_data.get("bio", "")
        )
        
        if foto_base64:
            try:
                # Decodificar la imagen base64
                formato, imgstr = foto_base64.split(';base64,') if ';base64,' in foto_base64 else ('', foto_base64)
                ext = formato.split('/')[-1] if formato else 'jpg'
                datos = ContentFile(base64.b64decode(imgstr))
                
                # Guardar la imagen
                file_name = f"{usuario.nombre_usuario}_profile.{ext}"
                usuario.foto_perfil.save(file_name, datos, save=True)
            except Exception as e:
                print(f"Error al procesar la foto: {e}")
        
        return usuario

